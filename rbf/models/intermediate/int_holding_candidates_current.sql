-- int view of all aircraft ('assumed' since stg is categories 0-6) active holdings
-- defines live holding candidates from calc layer

-- recency guard to protect against stale icao/flights/rows in the calculation layer
with active_flights as (
    select * from {{ ref('int_flight_patterns_calc')}}
    where fetched_at > {{ dbt.current_timestamp() }} - interval '3 minutes'
),

-- grab latest row per active flight
flights_latest as (
    select *, 
    row_number() over (partition by icao24 order by fetched_at DESC) as latest
    from active_flights
),

-- filter for qualifying candidates 
holding_candidates as (
    select * from flights_latest
    where latest = 1
    and fetches_in_window >= 4 -- one lap takes about 4 minutes
    and turns_started >= 3 -- require a full lap and another started, at least
    and distinct_turn_signs = 1
    and minutes_straight >= 2 -- protects against rapid +/- 10 degree heading changes as turns_started wouldnt catch
    and total_degrees_changed between 360 and 1800 -- corrected total degree changes remain plausible in the 15 minute window, 4 laps = about 16 minutes
    and altitude_range < 150 -- altitude change range remains low in the 5 minute window
    and max_abs_vertical_rate < 3 -- vertical rate stays under 3 m/s (about 590 ft/min) holding in the 5 minute window
)

select * from holding_candidates