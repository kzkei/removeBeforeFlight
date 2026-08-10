-- assumed emissions based on flight state via aircraft category (0,1) and (2,3,4,5,6) 
-- 0 = No information at all
-- 1 = No ADS-B Emitter Category Information

-- overwrite table materialization to incremental, add composite key for uniqueness, and schema change handling for possible new/modified columns
{{ config(
    materialized = 'incremental',
    unique_key = ['icao24', 'fetched_at'],
    on_schema_change = 'sync_all_columns' 
) }}

with all_emissions as (
    select * from {{ ref('int_flight_emissions_calc') }}

    -- incremental filter to only process new records
    {% if is_incremental() %}
    where fetched_at > (select max(fetched_at) from {{ this }})
    {% endif %}
),

emissions_assumed as (
    select
        {{ all_telemetry() }}
    from all_emissions
    where category in (0,1,2,3,4,5,6) -- include unknown aircraft category ints among fixed-wing aircraft ints
)

select * from emissions_assumed