with source as (

    select * from {{ source('raw', 'hpd_requests')}}
),

renamed as (

    select
        unique_key,
        created_date,
        closed_date,
        upper(trim(complaint_type)) as complaint_type,
        upper(trim(descriptor))     as descriptor,
        location_type,
        upper(trim(borough))        as borough,
        incident_zip,
        community_board,
        status,
        open_data_channel_type      as channel,
        latitude,
        longitude,
        date_diff('second', created_date, closed_date) / 3600.0 as durasi_jam

    from source
)


select * from renamed