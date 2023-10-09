import aiohttp
import asyncio
import logging

from typing import Optional, Tuple, Any
from datetime import datetime, timedelta
from aiohttp import ClientSession

from .settings import Settings
from .db import get_client
from ..utils.account import detect_address


logger = logging.getLogger(__name__)


async def get_mc_seqno(session: ClientSession, settings: Settings):
    # get masterchain last block
    payload = {'id': '1', 'jsonrpc': '2.0', 'method': 'getMasterchainInfo', 'params': {}}
    async with session.post(url=str(settings.ton_http_api.url), json=payload) as res:
        data = await res.json()
        if res.status != 200:
            raise RuntimeError(f'Failed with code {res.status}: {data}')
        seqno = data['result']['last']['seqno']
    return seqno


async def get_block_utime(seqno: int, session: ClientSession, settings: Settings):    
    # get shards
    payload = {'id': '1', 
               'jsonrpc': '2.0', 
               'method': 'getBlockHeader', 
               'params': {'workchain': -1, 'shard': -9223372036854775808, 'seqno': seqno}}
    async with session.post(url=str(settings.ton_http_api.url), json=payload) as res:
        data = await res.json()
        if res.status != 200:
            raise RuntimeError(f'Failed with code {res.status}: {data}')
        result = data['result']['gen_utime']
    return result


async def get_num_shards(seqno: int, session: ClientSession, settings: Settings):    
    # get shards
    payload = {'id': '1', 'jsonrpc': '2.0', 'method': 'shards', 'params': {'seqno': seqno}}
    async with session.post(url=str(settings.ton_http_api.url), json=payload) as res:
        data = await res.json()
        if res.status != 200:
            raise RuntimeError(f'Failed with code {res.status}: {data}')
        num_shards = len(data['result']['shards'])
    return num_shards


async def get_counter(session: ClientSession, settings: Settings):
    # get masterchain last block
    address = detect_address(settings.counter_address)['raw_form']
    params = {
        'address': address,
        'method': 'get_counter',
        'stack': []
    }
    payload = {'id': '1', 'jsonrpc': '2.0', 'method': 'runGetMethod', 'params': params}
    async with session.post(url=str(settings.ton_http_api.url), json=payload) as res:
        data = await res.json()
        if res.status != 200:
            raise RuntimeError(f'Failed with code {res.status}: {data}')
        counter_value = int(data['result']['stack'][0][1], 0)
    return counter_value


async def metrics_task(settings: Settings, prev_record: Optional[Tuple[Any]]=None):
    headers = None
    if settings.ton_http_api.api_token:
        headers = {'X-API-Key': settings.ton_http_api.api_token}
    
    async with ClientSession(headers=headers) as session:
        is_new_block = False
        while not is_new_block:
            seqno = await get_mc_seqno(session, settings=settings)
            if not prev_record or prev_record[0] != seqno:
                is_new_block = True
            else:
                await asyncio.sleep(1.0 / settings.rps)
        
        gen_utime_task = get_block_utime(seqno, session=session, settings=settings)
        shards_task = get_num_shards(seqno, session, settings=settings)
        counter_task = get_counter(session, settings=settings)
        cur_gen_utime, cur_shards, cur_tx = await asyncio.gather(*[gen_utime_task, shards_task, counter_task], return_exceptions=False)
    
    delta_utime = 1
    delta_tx = 0
    if prev_record:
        prev_seqno, prev_gen_utime, prev_tx = prev_record
        delta_utime = cur_gen_utime - prev_gen_utime
        delta_tx = cur_tx - prev_tx

    # insert results
    timestamp = datetime.utcnow()
    client = get_client(settings.database)
    data = [seqno, cur_gen_utime, timestamp, cur_shards, cur_tx, delta_utime, delta_tx]
    column_names = ['seqno', 'gen_utime', 'timestamp', 'shard_count', 'tx_count', 'gen_utime_delta', 'tx_count_delta']
    client.insert('history', 
                  data=[data], 
                  column_names=column_names)

    # logs
    logger.info(f'{data}')
    return (seqno, cur_gen_utime, cur_tx)
