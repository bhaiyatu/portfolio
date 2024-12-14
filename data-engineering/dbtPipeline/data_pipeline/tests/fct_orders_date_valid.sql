select
    *
from
    {{ ref('fct_orders')}}
where
    order_date > CURRENT_DATE()
    or order_date < date('1992-01-01')