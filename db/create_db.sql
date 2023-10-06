create table shards
(
    record_id        bigserial
        constraint shards_pk
            primary key,
    record_timestamp timestamp with time zone,
    value            integer
);

create index shards_record_timestamp_index
    on shards (record_timestamp);

create table tps
(
    record_id        bigserial
        constraint tps_pk
            primary key,
    record_timestamp timestamp with time zone,
    value            integer,
    counter          bigint
);

create index tps_record_timestamp_index
    on tps (record_timestamp);