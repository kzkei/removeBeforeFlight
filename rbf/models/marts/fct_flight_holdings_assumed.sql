-- fct table of current holdings: categories {0,1,2,3,4,5,6}


with holding_candidates_assumed as (
    select * from {{ ref('int_holding_candidates_current') }}
)

select * from holding_candidates_assumed
