with source as (
    SELECT
        endereco_local_votacao,
        municipio_local_votacao,
        uf_local_votacao,
        REPLACE(postcode, '-', '') as postcode
    FROM "eleicoes_2022"."secoes_enriched_addresses"
    where postcode is not null and length(postcode) = 9
),
renamed as (
    select
        endereco_local_votacao as ENDERECO,
        municipio_local_votacao as MUNICIPIO,
        uf_local_votacao as UF,
        postcode as CEP
    from source
),
final as (
    select
        *
    from renamed
    group by 1, 2, 3, 4
)
select * from source
