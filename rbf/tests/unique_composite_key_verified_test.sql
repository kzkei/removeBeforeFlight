{# 
-- duplicate row testing on verified emissions table

-- select icao24, fetched_at, count(*) as duplicate_count
-- from {{ ref 'fct_flight_emissions_verified' }}
-- group by icao24, fetched_at
-- having count(*) > 1

-- return duplicates if any (icao24, fetched_at)
#}

{{ composite_test_query('fct_flight_emissions_verified') }}