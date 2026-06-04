with flights as (
    select * from {{ ref('stg_flight_states') }}
),

-- reasonabkle approximation of real emissions based on flight state data and ICAO fuel burn factors
emissions as (
    select
        -- flight identifiers
        id,
        icao24,
        callsign,
        origin_country,

        -- positions/times
        longitude,
        latitude,
        baro_altitude,
        last_contact_at,
        fetched_at,

        -- flight dynamics
        velocity,
        vertical_rate,
        true_track,

        -- aircraft state
        position_source,
        category,

        -- co2 estimation (ICAO simplified fuel burn method)
        -- baseline: commercial jet burns ~3.5kg fuel/km at cruise
        -- CO2 = fuel_kg * 3.16 (ICAO carbon factor)
        -- velocity is in m/s, convert to km/h for readability
        round((velocity * 3.6)::numeric, 2)                    as velocity_kmh,

        -- estimated fuel burn rate kg/s based on altitude regime
        case
            when baro_altitude >= 8000 then 0.85  -- cruise
            when baro_altitude >= 3000 then 1.10  -- climb/descent
            else 1.40                              -- low altitude
        end                                                     as fuel_burn_rate_kg_s,

        -- estimated co2 kg/s = fuel burn rate * 3.16
        round(
            (case
                when baro_altitude >= 8000 then 0.85
                when baro_altitude >= 3000 then 1.10
                else 1.40
            end * 3.16)::numeric
        , 4)                                                    as co2_kg_s

    from flights
    where velocity is not null
    and baro_altitude is not null
)

select * from emissions