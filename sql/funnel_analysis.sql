
USE ecommerce_analytics;



-- Identify the first view event for each session.
-- This establishes the entry point for the conversion funnel.
WITH views as (
	SELECT session_id,
            MIN(event_order) AS view_order
	FROM session_level_funnel_stage
    WHERE event_type = 'view'
    GROUP BY session_id
), 


-- Identify the first add-to-cart event occurring after a view.
-- Sessions without a preceding view are excluded.
carts AS (
	SELECT S.session_id, MIN(S.event_order) 
    AS cart_order
    FROM session_level_funnel_stage AS S
    INNER JOIN views AS V ON S.session_id = V.session_id
    WHERE S.event_type = 'add_to_cart'
    AND S.event_order > V.view_order
    GROUP BY S.session_id
), 



-- Identify the first checkout event occurring after an add to cart.
-- Only sessions that reached the cart stage are considered.
checkouts AS (
	SELECT S.session_id, MIN(S.event_order) 
    AS checkout_order
    FROM session_level_funnel_stage AS S
    INNER JOIN carts AS C ON S.session_id = C.session_id
    WHERE S.event_type = 'checkout'
    AND S.event_order > C.cart_order
    GROUP BY S.session_id
), 


-- Identify the first purchase event occurring after checkout.
-- Only sessions that reached the checkout stage are considered.
purchases AS (
	SELECT S.session_id, MIN(S.event_order) 
    AS purchase_order
    FROM session_level_funnel_stage AS S 
    INNER JOIN checkouts AS C ON S.session_id = C.session_id
    WHERE S.event_type = 'purchase'
    AND S.event_order > C.checkout_order
    GROUP BY S.session_id
),


-- Find the position of the first event with a nonblank device value
-- for each session. This allows each session to be assigned a
-- consistent device category.
first_device_order AS (
	SELECT session_id, MIN(event_order) AS min_device_order
	FROM session_level_funnel_stage
    WHERE NULLIF(TRIM(device), '') IS NOT NULL
    GROUP BY session_id
), 


-- Find the position of the first event with a nonblank traffic source
-- for each session.
first_traffic_source_order AS (
	SELECT session_id, MIN(event_order) AS min_traffic_order
    FROM session_level_funnel_stage 
    WHERE NULLIF(TRIM(traffic_source), '') IS NOT NULL
    GROUP BY session_id
),


-- Assign one device and one traffic source to each session.
-- Use the earliest available nonblank value for each attribute.
-- Replace missing or blank values with 'unknown'.
session_attributes AS (
	SELECT S.session_id, COALESCE(NULLIF(TRIM(S1.device), ''), 'unknown') AS device, 
			COALESCE(NULLIF(TRIM(S2.traffic_source), ''), 'unknown') AS traffic_source
    FROM (SELECT DISTINCT session_id FROM session_level_funnel_stage) AS S
    LEFT JOIN first_device_order AS D ON S.session_id = D.session_id
	LEFT JOIN session_level_funnel_stage AS S1 ON D.session_id = S1.session_id
    AND D.min_device_order = S1.event_order
    LEFT JOIN first_traffic_source_order AS T ON S.session_id = T.session_id
    LEFT JOIN session_level_funnel_stage AS S2 ON T.session_id = S2.session_id
    AND S2.event_order = T.min_traffic_order
),

-- =========================================================
-- FUNNEL BY DEVICE
-- =========================================================

-- Create one record per session with its device and indicators
-- showing whether it reached each funnel stage.
-- Each indicator is 1 if the session reached the stage and 0 otherwise.
session_device_info AS (
	SELECT S.session_id, S.device, 
			(CASE WHEN V.session_id IS NOT NULL THEN 1 ELSE 0 END) 
            AS sessions_with_view, 
            (CASE WHEN C.session_id IS NOT NULL THEN 1 ELSE 0 END) 
            AS sessions_with_cart, 
            (CASE WHEN CH.session_id IS NOT NULL THEN 1 ELSE 0 END) 
            AS sessions_with_checkout, 
            (CASE WHEN P.session_id IS NOT NULL THEN 1 ELSE 0 END) 
            AS sessions_with_purchase
    FROM session_attributes AS S
    LEFT JOIN views AS V ON S.session_id = V.session_id
    LEFT JOIN carts AS C ON S.session_id = C.session_id
    LEFT JOIN checkouts AS CH ON S.session_id = CH.session_id
    LEFT JOIN purchases AS P ON S.session_id = P.session_id
),


-- Aggregate the session indicators to obtain funnel-stage counts
-- for each device category.
device_counts AS (
	SELECT device, SUM(sessions_with_view) AS sessions_with_view, 
			SUM(sessions_with_cart) AS sessions_with_cart, 
			SUM(sessions_with_checkout) AS sessions_with_checkout, 
			SUM(sessions_with_purchase) AS sessions_with_purchase
	FROM session_device_info 
	GROUP BY device
),


-- Calculate conversion rates for each device.
-- Stage-to-stage rates use the preceding stage as the denominator.
-- View-to-purchase rate measures the overall funnel conversion rate.
rates_by_device AS (
	SELECT device, ROUND(sessions_with_cart * 1.0 / NULLIF(sessions_with_view, 0) * 100, 2)
		AS view_to_cart_rate, 
        ROUND(sessions_with_checkout * 1.0 / NULLIF(sessions_with_cart, 0) * 100.0, 2)
        AS cart_to_checkout_rate, 
        ROUND(sessions_with_purchase * 1.0 / NULLIF(sessions_with_checkout, 0) * 100.0, 2)
        AS checkout_to_purchase_rate, 
        ROUND(sessions_with_purchase * 1.0 / NULLIF(sessions_with_view, 0) * 100.0, 2) 
        AS view_to_purchase_rate, 
        sessions_with_view, sessions_with_cart, 
        sessions_with_checkout, sessions_with_purchase
	FROM device_counts
),


-- =========================================================
-- FUNNEL BY TRAFFIC SOURCE
-- =========================================================

-- Create one record per session with its traffic source and
-- indicators showing whether it reached each funnel stage.
session_traffic_source_info AS (
	SELECT S.session_id, S.traffic_source, 
			(CASE WHEN V.session_id IS NOT NULL THEN 1 ELSE 0 END) 
            AS sessions_with_view, 
            (CASE WHEN C.session_id IS NOT NULL THEN 1 ELSE 0 END) 
            AS sessions_with_cart, 
            (CASE WHEN CH.session_id IS NOT NULL THEN 1 ELSE 0 END) 
            AS sessions_with_checkout, 
            (CASE WHEN P.session_id IS NOT NULL THEN 1 ELSE 0 END) 
            AS sessions_with_purchase
    FROM session_attributes AS S
    LEFT JOIN views AS V ON S.session_id = V.session_id
    LEFT JOIN carts AS C ON S.session_id = C.session_id
    LEFT JOIN checkouts AS CH ON S.session_id = CH.session_id
    LEFT JOIN purchases AS P ON S.session_id = P.session_id
), 


-- Aggregate funnel-stage counts for each traffic source.
traffic_source_counts AS (
	SELECT traffic_source, SUM(sessions_with_view) AS sessions_with_view, 
			SUM(sessions_with_cart) AS sessions_with_cart, 
			SUM(sessions_with_checkout) AS sessions_with_checkout, 
			SUM(sessions_with_purchase) AS sessions_with_purchase
	FROM session_traffic_source_info 
	GROUP BY traffic_source
),


-- Calculate stage-to-stage and overall conversion rates
-- for each traffic source, using the same definitions as
-- the device-level analysis.
rates_by_traffic_source AS (
	SELECT traffic_source, ROUND(sessions_with_cart * 1.0 / NULLIF(sessions_with_view, 0) * 100, 2)
		AS view_to_cart_rate, 
        ROUND(sessions_with_checkout * 1.0 / NULLIF(sessions_with_cart, 0) * 100.0, 2)
        AS cart_to_checkout_rate, 
        ROUND(sessions_with_purchase * 1.0 / NULLIF(sessions_with_checkout, 0) * 100.0, 2)
        AS checkout_to_purchase_rate, 
        ROUND(sessions_with_purchase * 1.0 / NULLIF(sessions_with_view, 0) * 100.0, 2) 
        AS view_to_purchase_rate, 
        sessions_with_view, sessions_with_cart, 
        sessions_with_checkout, sessions_with_purchase
	FROM traffic_source_counts
)
     
     
SELECT *
FROM rates_by_device;

SELECT *
FROM rates_by_traffic_source;






