{{ config(severity='warn') }}

select *
from {{ ref('stg_hpd_requests') }}
where durasi_jam < 0