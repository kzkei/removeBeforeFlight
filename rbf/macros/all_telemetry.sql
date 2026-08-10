{% macro all_telemetry() %}
    id, icao24, callsign, origin_country,
    longitude, latitude, baro_altitude, last_contact_at, fetched_at,
    velocity, vertical_rate, true_track,
    position_source, category,
    velocity_kmh, fuel_burn_rate_kg_s, co2_kg_s
{% endmacro %}