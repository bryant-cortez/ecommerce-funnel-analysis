
USE ecommerce_analytics;

-- Calculate overall revenue, completed order count, and average order value (AOV).
WITH completed_order_info AS (
	SELECT SUM(total_amount) AS total_revenue, 
			COUNT(*) AS completed_orders, 
            ROUND(SUM(total_amount) / COUNT(*), 2) AS average_order_value
	FROM orders
    WHERE order_status = 'completed'
), 


-- Rank nonblank device values chronologically within each session
-- to identify the first recorded device.

ranked_session_device AS (
    SELECT
        session_id, device,
        ROW_NUMBER() OVER (
            PARTITION BY session_id
            ORDER BY event_order ASC
        ) AS rn
    FROM session_level_funnel_stage
    WHERE device IS NOT NULL
      AND TRIM(device) != ''
),


-- Retain the earliest nonblank device value for each session.
session_device AS (
    SELECT
        session_id, device
    FROM ranked_session_device
    WHERE rn = 1
), 

-- Aggregate completed-order revenue, order count, and AOV by device.
device_totals AS (
	SELECT S.device, SUM(O.total_amount) AS total_revenue, 
			COUNT(*) AS completed_orders, 
            ROUND(SUM(O.total_amount) / COUNT(*), 2) AS average_order_value
    FROM orders AS O
    INNER JOIN session_device AS S ON O.session_id = S.session_id
    WHERE O.order_status = 'completed'
    GROUP BY S.device
), 


-- Rank nonblank traffic source values chronologically within each session
-- to identify the first recorded traffic source.
ranked_session_traffic_source AS (
	SELECT session_id, traffic_source, 
			ROW_NUMBER() OVER (
            PARTITION BY session_id
            ORDER BY event_order ASC
            ) AS rn 
	FROM session_level_funnel_stage
    WHERE traffic_source IS NOT NULL
      AND TRIM(traffic_source) != ''
), 


-- Retain the earliest nonblank traffic source for each session.
session_traffic_source AS (
	SELECT session_id, traffic_source
    FROM ranked_session_traffic_source
    WHERE rn = 1
),


-- Aggregate completed-order revenue, order count, and AOV by traffic source.
traffic_source_totals AS (	
	SELECT S.traffic_source, SUM(O.total_amount) AS total_revenue, 
			COUNT(*) AS completed_orders, 
            ROUND(SUM(O.total_amount) / COUNT(*), 2) AS average_order_value
    FROM orders AS O 
    INNER JOIN session_traffic_source AS S ON O.session_id = S.session_id
    WHERE O.order_status = 'completed'
    GROUP BY S.traffic_source
), 


-- Count unique social sessions that reached the view stage.
social_views AS (
	SELECT COUNT(DISTINCT session_id) AS social_view_count
    FROM session_level_funnel_stage
    WHERE LOWER(traffic_source) = 'social'
    AND event_type = 'view'
), 

-- Count unique social sessions that progressed from viewing a product
-- to adding a product to the cart.
social_carts AS (
	SELECT COUNT(DISTINCT V.session_id) AS social_cart_count
    FROM session_level_funnel_stage AS V
    INNER JOIN session_level_funnel_stage AS C ON V.session_id = C.session_id 
    AND V.event_order < C.event_order
    WHERE LOWER(V.traffic_source) = 'social'
    AND V.event_type = 'view'
    AND C.event_type = 'add_to_cart'
), 


-- Count unique non-social sessions that reached the view stage.
-- These sessions provide the benchmark population.
non_social_views AS (
	SELECT COUNT(DISTINCT session_id) AS non_social_view_count
    FROM session_level_funnel_stage
    WHERE (LOWER(traffic_source) != 'social' OR traffic_source IS NULL)
    AND event_type = 'view'
), 


-- Count unique non-social sessions that progressed from viewing a product
-- to adding a product to the cart.
non_social_carts AS (
	SELECT COUNT(DISTINCT V.session_id) AS non_social_cart_count
    FROM session_level_funnel_stage AS V
    INNER JOIN session_level_funnel_stage AS C ON V.session_id = C.session_id
    AND V.event_order < C.event_order
    WHERE (LOWER(V.traffic_source) != 'social' OR V.traffic_source IS NULL)
    AND V.event_type = 'view'
    AND C.event_type = 'add_to_cart'
),


-- Count unique social sessions that completed the full sequential funnel:
-- view -> add to cart -> checkout -> purchase.
social_purchases AS (
	SELECT COUNT(DISTINCT V.session_id) AS social_purchase_count
    FROM session_level_funnel_stage AS V
    INNER JOIN session_level_funnel_stage AS C
    ON V.session_id = C.session_id AND V.event_order < C.event_order
    INNER JOIN session_level_funnel_stage AS CH 
    ON C.session_id = CH.session_id AND C.event_order < CH.event_order
    INNER JOIN session_level_funnel_stage AS P 
    ON CH.session_id = P.session_id AND CH.event_order < P.event_order
    WHERE LOWER(V.traffic_source) = 'social'
    AND V.event_type = 'view'
    AND C.event_type = 'add_to_cart'
    AND CH.event_type = 'checkout'
    AND P.event_type = 'purchase'
), 


-- Calculate actual social view-to-cart conversion and the pooled
-- non-social benchmark conversion rate.
-- Estimate expected social carts and additional purchases by applying
-- the benchmark rate while holding subsequent conversion constant.
social_improvement AS (
    SELECT
        SV.social_view_count, SC.social_cart_count,
        SP.social_purchase_count, NSV.non_social_view_count,
        NSC.non_social_cart_count,

        SC.social_cart_count * 1.0
            / SV.social_view_count AS actual_social_conversion,

        NSC.non_social_cart_count * 1.0
            / NSV.non_social_view_count AS benchmark_conversion,

        SP.social_purchase_count * 1.0
            / SC.social_cart_count AS social_cart_purchase_rate,

        SV.social_view_count * 1.0
            * NSC.non_social_cart_count
            / NSV.non_social_view_count AS expected_social_carts,

        SP.social_purchase_count * 1.0
            / SC.social_cart_count
            *
            (
                SV.social_view_count * 1.0
                * NSC.non_social_cart_count
                / NSV.non_social_view_count
                - SC.social_cart_count
            ) AS additional_purchases

    FROM social_views AS SV
    CROSS JOIN social_carts AS SC
    CROSS JOIN social_purchases AS SP
    CROSS JOIN non_social_views AS NSV
    CROSS JOIN non_social_carts AS NSC
),


-- Present the social improvement scenario results as readable metrics.
-- Estimate additional revenue using the calculated overall AOV.
social_impact AS (
	SELECT
		SI.social_view_count, SI.social_cart_count, SI.social_purchase_count,
		ROUND(SI.actual_social_conversion * 100, 2)
			AS actual_social_conversion_pct,
		ROUND(SI.benchmark_conversion * 100, 2)
			AS benchmark_conversion_pct,
		ROUND(SI.expected_social_carts, 0)
			AS expected_social_carts,
		ROUND(SI.expected_social_carts - SI.social_cart_count, 0)
			AS additional_carts,
		ROUND(SI.social_cart_purchase_rate * 100, 2)
			AS social_cart_purchase_pct,
		ROUND(SI.additional_purchases, 0)
			AS additional_purchases,
		ROUND(SI.additional_purchases * COI.average_order_value, 2)
			AS estimated_additional_revenue
	FROM social_improvement AS SI
    CROSS JOIN completed_order_info AS COI
), 


-- Count unique tablet sessions that progressed through the funnel
-- and reached checkout.
tablet_checkouts AS (
    SELECT COUNT(DISTINCT V.session_id) AS tablet_checkout_count
    FROM session_level_funnel_stage AS V
    INNER JOIN session_level_funnel_stage AS C 
	ON V.session_id = C.session_id 
	AND V.event_order < C.event_order
    INNER JOIN session_level_funnel_stage AS CH
    ON C.session_id = CH.session_id
    AND C.event_order < CH.event_order
    WHERE LOWER(V.device) = 'tablet'
	AND V.event_type = 'view'
    AND C.event_type = 'add_to_cart'
	AND CH.event_type = 'checkout'
),


-- Count unique tablet sessions that completed the full sequential funnel:
-- view -> add to cart -> checkout -> purchase.
tablet_purchases AS (
    SELECT COUNT(DISTINCT V.session_id) AS tablet_purchase_count
    FROM session_level_funnel_stage AS V
    INNER JOIN session_level_funnel_stage AS C 
	ON V.session_id = C.session_id 
	AND V.event_order < C.event_order
	INNER JOIN session_level_funnel_stage AS CH
    ON C.session_id = CH.session_id
    AND C.event_order < CH.event_order
    INNER JOIN session_level_funnel_stage AS P 
	ON CH.session_id = P.session_id 
	AND CH.event_order < P.event_order
    WHERE LOWER(V.device) = 'tablet'
	AND V.event_type = 'view'
	AND C.event_type = 'add_to_cart'
    AND CH.event_type = 'checkout'
	AND P.event_type = 'purchase'
),


-- Count desktop and mobile sessions that reached checkout.
-- These sessions form the comparison benchmark population.
desktop_mobile_checkouts AS (
    SELECT COUNT(DISTINCT V.session_id) AS benchmark_checkout_count
    FROM session_level_funnel_stage AS V
    INNER JOIN session_level_funnel_stage AS C 
        ON V.session_id = C.session_id 
        AND V.event_order < C.event_order
    INNER JOIN session_level_funnel_stage AS CH
        ON C.session_id = CH.session_id
        AND C.event_order < CH.event_order
    WHERE LOWER(V.device) IN ('desktop', 'mobile')
      AND V.event_type = 'view'
      AND C.event_type = 'add_to_cart'
      AND CH.event_type = 'checkout'
),


-- Count desktop and mobile sessions that completed the full sequential funnel.
-- Used to calculate the pooled checkout-to-purchase benchmark.
desktop_mobile_purchases AS (
    SELECT COUNT(DISTINCT V.session_id) AS benchmark_purchase_count
    FROM session_level_funnel_stage AS V
    INNER JOIN session_level_funnel_stage AS C 
        ON V.session_id = C.session_id 
        AND V.event_order < C.event_order
    INNER JOIN session_level_funnel_stage AS CH
        ON C.session_id = CH.session_id
        AND C.event_order < CH.event_order
    INNER JOIN session_level_funnel_stage AS P 
        ON CH.session_id = P.session_id 
        AND CH.event_order < P.event_order
    WHERE LOWER(V.device) IN ('desktop', 'mobile')
      AND V.event_type = 'view'
      AND C.event_type = 'add_to_cart'
      AND CH.event_type = 'checkout'
      AND P.event_type = 'purchase'
),


-- Calculate actual tablet checkout-to-purchase conversion and the pooled
-- desktop/mobile benchmark rate.
-- Estimate expected tablet purchases and additional purchases
-- if tablets achieved the benchmark conversion rate.
tablet_improvement AS (
    SELECT
        TC.tablet_checkout_count, TP.tablet_purchase_count, DMC.benchmark_checkout_count,
        DMP.benchmark_purchase_count,

        TP.tablet_purchase_count * 1.0 
            / TC.tablet_checkout_count AS actual_tablet_conversion,

        DMP.benchmark_purchase_count * 1.0 
            / DMC.benchmark_checkout_count AS benchmark_conversion,

        TC.tablet_checkout_count * 1.0
            * DMP.benchmark_purchase_count
            / DMC.benchmark_checkout_count AS expected_tablet_purchases,

        (TC.tablet_checkout_count * 1.0
            * DMP.benchmark_purchase_count
            / DMC.benchmark_checkout_count)
            - TP.tablet_purchase_count AS additional_purchases

    FROM tablet_checkouts AS TC
    CROSS JOIN tablet_purchases AS TP
    CROSS JOIN desktop_mobile_checkouts AS DMC
    CROSS JOIN desktop_mobile_purchases AS DMP
),


-- Present the tablet improvement scenario results as readable metrics.
-- Estimate additional revenue using the calculated overall AOV.
tablet_impact AS (
    SELECT
        TI.tablet_checkout_count,
        TI.tablet_purchase_count,
        ROUND(TI.actual_tablet_conversion * 100, 2) 
        AS actual_tablet_conversion_pct,
        ROUND(TI.benchmark_conversion * 100, 2) 
        AS benchmark_conversion_pct,
        ROUND(TI.expected_tablet_purchases, 0) 
        AS expected_tablet_purchases,
        ROUND(TI.additional_purchases, 0) 
        AS additional_purchases,
        ROUND(TI.additional_purchases * COI.average_order_value, 2) 
        AS estimated_additional_revenue
    FROM tablet_improvement AS TI
    CROSS JOIN completed_order_info AS COI
)

SELECT * 
FROM social_impact;

SELECT *
FROM tablet_impact;






















































