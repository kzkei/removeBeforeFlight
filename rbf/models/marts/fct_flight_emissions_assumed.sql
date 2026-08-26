-- assumed emissions (all) from int_flight_emissions_calc
-- 0 = No information at all
-- 1 = No ADS-B Emitter Category Information

-- overwrite table materialization to incremental, add composite key for uniqueness, and schema change handling for possible new/modified columns
{{ config(
    materialized = 'incremental',
    unique_key = ['icao24', 'fetched_at'],
    on_schema_change = 'sync_all_columns' 
) }}

with assumed_emissions as (
    select * from {{ ref('int_flight_emissions_calc') }}

    -- incremental filter to only process new records
    {% if is_incremental() %}
    where fetched_at > (select max(fetched_at) from {{ this }})
    {% endif %}
)

select * from assumed_emissions