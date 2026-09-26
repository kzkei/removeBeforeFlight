-- intermediate model to calculate rolling flight metrics for identifying holding patterns
-- used in fct_active_holdings_assumed and verfied tables
-- data fetched every minute

-- delete+insert (merge) incremental strategy -> append only new records, preserve history

{{ config (
    materialized = 'incremental',
    incremental_strategy = 'delete+insert',
    unique_key = ['icao24', 'fetched_at'],
    on_schema_change = 'sync_all_columns'
)}}

-- filter to the last 25 minutes of staged data for rolling-window calculations
with flights as (
    select * from {{ ref('stg_flight_states') }}
    where fetched_at > {{ dbt.current_timestamp() }} - interval '25 minutes'
),

-- gather raw true_track changes, find the shortest signed angular change (circular) in true_track between minute fetches, classify the change/turn direction by sign, identify the start of turns

-- -- add to window: raw heading changes from most recent row - previous row on all icaos
raw_heading_changes as (
    select 
        *,
        case
            when fetched_at - lag(fetched_at, 1) over (
                partition by icao24 order by fetched_at
            ) > interval '5 minutes'
            then null -- if no previous record exists within last 5 minutes for specified icao24 then keep null in case of icao24 reuse
            else true_track - lag(true_track, 1) over (
                partition by icao24 order by fetched_at
            )
        end as raw_delta
    from flights
),

-- -- add to window: shortest signed angular changes (most reasonable turns)
corrected_heading_changes as (
    select 
        *,
        case -- when the difference between true_track absolute values is greater than 180 dg, we need to correct for the circular nature of heading values and take shortest signed angular change
                -- 300 - 10 = 290, but the actual (most reasonable) change is -70 dg (10 -> 300)
                -- 350 - 10 = 340, but the actual change is -20 dg (10 -> 350)
                -- 30 - 350 = -320, but the actual change is +40 dg (350 -> 30)
                -- 60 - 150 = -90, no correction needed, < 180 dg
                -- 60 - 275 = -215, but the actual change is +145 dg (275 -> 60) 
            when raw_delta > 180 then raw_delta - 360
            when raw_delta < -180 then raw_delta + 360  -- -215 + 360
            else raw_delta -- keep raw if absolute value of raw_delta is not > 180, also if no previous record exists for specified icao24 then keep null
        end as corrected_delta
    from raw_heading_changes
),

-- -- add to window: turn direction organized by sign, near zero changes within the last minute are indicators of straight flight
classified_turns as (
    select 
        *,
        case 
            when corrected_delta > 10.0 then 1      -- right
            when corrected_delta < -10.0 then -1    -- left
            when corrected_delta is null then null  -- null for boundary case of no previous record for specified icao24
            else 0                                  -- straight
        end as turn_sign
    from corrected_heading_changes
),

-- -- add to window: turn flag where heading delta sign is not 0 and the previous records heading delta sign IS 0 (i.e. turn occured from straight flight)
distinct_turns as (
    select
        *,
        case
            when turn_sign != 0
                and lag(turn_sign, 1, turn_sign) over (
                    partition by icao24 order by fetched_at
                ) = 0
            then 1
            when turn_sign is null 
            then null -- keep boundary case as unknown/null
            else 0
        end as turn_flag -- flag by '1' if noticable turn occured between the records
    from classified_turns
),

-- gather mutiple factors for each icao24 under restricted window (15 mins), calculate metrics for each icao24 in window
flight_metrics_over_window as (
    select
        *,
        -- count of fetches that fall within w15
        count(*) over w15 as fetches_in_window,

        -- minutes and turns: gather turn segments over w15, evaluate number of distinct turn signs in w15, count minutes of straight flight (guard)
        sum(turn_flag) over w15 as turns_started,

        -- evaluate turn consistency over window: only the active turns (1 and -1), ignoring 0
        case 
            when min(nullif(turn_sign, 0)) over w15 is null
            then 0
            when min(nullif(turn_sign, 0)) over w15 != max(nullif(turn_sign, 0)) over w15
            then 2 -- both left (-1) and right (1) turns happened in this window
            else 1 -- only one turning direction happened in this window
        end as distinct_turn_signs,

        -- minutes of straight flight over the window
        sum(case
                when turn_sign = 0 
                then 1 
                else 0 
            end) over w15
        as minutes_straight,

        -- bounded position check: spread of lat/lon over the window
        max(latitude) over w15 - min(latitude) over w15 as lat_spread,
        max(longitude) over w15 - min(longitude) over w15 as lon_spread,

        -- total degrees changed: sum of absolute value of corrected deltas over the window, how much has the aircraft turned in total
        sum(abs(corrected_delta)) over w15 as total_degrees_changed,

        -- metrics for most recent 5 minutes of flight

        -- altitude stability / range: is the aircraft maintaining a consistent altitude or climbing/descending
        max(baro_altitude) over w5 - min(baro_altitude) over w5 as altitude_range,

        -- vertical rate stability: is the aircraft maintaining a consistent vertical rate or climbing/descending
        max(abs(vertical_rate)) over w5 as max_abs_vertical_rate

    from distinct_turns

    -- windows to discard 15+ and 5+ minute old fetches respectively, for targeted situation metrics
    window 
        w15 as (
            partition by icao24 order by fetched_at
            range between interval '15 minutes' preceding and current row
        ),

        w5 as (
            partition by icao24 order by fetched_at
            range between interval '5 minutes' preceding and current row
        )
)

-- implied_vs_actual as (
--     select *

--     -- need implied distance vs actual (velocity x time)
--     -- haversine formula for distance between two lat/lon points, how can i use a built in for this, or is postgis the move here
-- ),

-- output limited to new rows
-- only load rows newer than the target table's max fetched_at, avoid recomputing processed snapshots
select * from flight_metrics_over_window

{% if is_incremental() %}
where fetched_at > (select coalesce(max(fetched_at), '1900-01-01'::timestamp) from {{ this }})
{% endif %}
