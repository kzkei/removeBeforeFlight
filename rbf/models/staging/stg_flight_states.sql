with source as (
    select * from {{ source('removebeforeflight', 'raw_flight_states') }} -- source and table names
),

staged as (
    select
        -- identifiers
        id,
        icao24,
        trim(callsign) as callsign,
        origin_country,

        -- timestamps (cast unix to proper postgres timestamp)
        to_timestamp(time_position) as time_position_at,
        to_timestamp(last_contact)  as last_contact_at,
        fetched_at,

        -- positions
        longitude,
        latitude,
        baro_altitude,
        geo_altitude,
        on_ground,

        -- flight dynamics
        velocity,
        true_track,
        vertical_rate,

        -- metadata
        squawk,
        spi,
        position_source,
        category,
        sensors

    from source
    where icao24 is not null
      and last_contact is not null
      and on_ground = false  -- only airborne flights for emissions
)

select * from staged