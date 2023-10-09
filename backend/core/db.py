from clickhouse_connect import get_client
from clickhouse_connect.driver import Client

from .settings import DatabaseSettings


def get_client(settings: DatabaseSettings):
    return clickhouse_connect.get_client(dsn=settings.clickhouse_dsn)


def create_tables(client: Client):
    sql = '''create table if not exists history(
        record_id UInt64,
        timestamp DateTime,
        transaction_count UInt64,
        shard_count UInt32,
        tps Float32
    )
    engine = MergeTree()
    primary key (record_id, timestamp)
    order by timestamp
    '''
    client.command(sql)