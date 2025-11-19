{% macro grant_select(role, schema=target.schema) %}
    {% set sql %}
        GRANT SELECT ON ALL TABLES IN SCHEMA {{ schema }} TO ROLE {{ role }};
        GRANT SELECT ON ALL VIEWS IN SCHEMA {{ schema }} TO ROLE {{ role }};
    {% endset %}

    {% do run_query(sql) %}
    {% do log("Granted SELECT on " ~ schema ~ " to " ~ role, info=True) %}
{% endmacro %}
