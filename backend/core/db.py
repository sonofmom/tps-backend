import clickhouse_connect
from clickhouse_connect.driver import Client
from clickhouse_connect.driver import httputil

from .settings import DatabaseSettings


big_pool_mgr = httputil.get_pool_manager(maxsize=256, num_pools=16)
def get_client(settings: DatabaseSettings):
    host = settings.clickhouse_dsn.hosts()[0]
    dbname = settings.clickhouse_dsn.path[1:]
    client = clickhouse_connect.get_client(host=host['host'],
                                           port=host['port'],
                                           user=host['username'],
                                           password=host['password'],
                                           database=dbname,
                                           pool_mgr=big_pool_mgr)
    return client


def create_tables(client: Client):
    sql = '''create table if not exists history(
        seqno UInt32,
        gen_utime UInt32,
        timestamp DateTime,
        shard_count UInt32,
        val_count UInt32,
        mc_val_count UInt32,
        tx_count UInt64,
        gen_utime_delta UInt32,
        tx_count_delta UInt32
    )
    engine = MergeTree()
    primary key (seqno, gen_utime)
    order by (seqno, gen_utime, timestamp)
    '''
    client.command(sql)
