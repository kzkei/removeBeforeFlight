-- fct table of current holdings: categories {2,3,4,5,6} / fixed-wing aircraft

with holding_candidates_verified as (
    select * from {{ ref('int_holding_candidates_current')}}
    where category in (2,3,4,5,6)
)

select * from holding_candidates_verified