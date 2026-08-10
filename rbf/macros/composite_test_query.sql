{% macro composite_test_query(model) %}
    select icao24, fetched_at, count(*) as duplicate_count
    from {{ ref(model) }}
    group by icao24, fetched_at
    having count(*) > 1
{% endmacro %}