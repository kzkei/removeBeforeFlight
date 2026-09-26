-- Intermediate model for filtering category by (2,3,4,5,6) / fixed-wing aircraft

with holding_verified as (
    select * from {{ ref('int_flight_patterns_calc')}}
    where category in (2,3,4,5,6)
)

select * from holding_verified