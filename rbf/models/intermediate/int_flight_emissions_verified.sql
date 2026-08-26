-- Intermediate model for filtering by ONLY (2,3,4,5,6) or fixed-wing aircraft
-- model used in 2 fct tables, verified emissions and holdings

with flights_verified as ( 
    select * from {{ ref('int_flight_emissions_calc') }}
    where category in (2,3,4,5,6)
)

select * from flights_verified

