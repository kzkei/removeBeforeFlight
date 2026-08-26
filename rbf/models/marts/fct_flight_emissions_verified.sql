-- verified emissions based on flight state via category (2,3,4,5,6 or fixed-wing aircraft)

-- overwrite table materialization to incremental, add composite key for uniqueness, and schema change handling for possible new/modified columns
{{ config(
    materialized = 'incremental',
    unique_key = ['icao24', 'fetched_at'],
    on_schema_change = 'sync_all_columns' 
) }}

with emissions_verified as (
    select * from {{ ref('int_flight_emissions_verified') }}

    -- incremental filter to only process new records
    {% if is_incremental() %}
    where fetched_at > (select max(fetched_at) from {{ this }})
    {% endif %}
)

select * from emissions_verified