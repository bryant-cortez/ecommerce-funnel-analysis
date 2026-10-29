
USE ecommerce_analytics;


-- Create a staging table containing valid event records
-- and assign each event a chronological position within its session.
CREATE TABLE session_level_funnel_stage AS
SELECT
    session_id,
    event_timestamp,
    event_id,
    event_type,
    device,
    traffic_source,
    ROW_NUMBER() OVER (
        PARTITION BY session_id
        ORDER BY event_timestamp ASC, event_id ASC
    ) AS event_order
FROM events
WHERE session_id IS NOT NULL
  AND event_timestamp IS NOT NULL
  AND event_type IS NOT NULL;
  
-- Numbers events sequentially within each session.
-- event_timestamp establishes chronological order.
-- event_id breaks ties when timestamps are identical. 
-- Exclude records missing the fields needed to identify
-- a session, establish event order, or classify the event.
