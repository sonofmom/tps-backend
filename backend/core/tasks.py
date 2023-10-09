import aiohttp
import asyncio
import logging

from aiohttp import ClientSession
from .settings import Settings


logger = logging.getLogger(__name__)


async def get_shards_data(session: ClientSession, settings: Settings):    
    # get masterchain last block
    payload = {'id': '1', 'jsonrpc': '2.0', 'method': 'getMasterchainInfo', 'params': {}}
    async with session.post(url=str(settings.ton_http_api.url), json=payload) as res:
        data = await res.json()
        if res.status != 200:
            raise RuntimeError(f'Failed with code {res.status}: {data}')
        seqno = data['result']['last']['seqno']
    
    logger.info(f'Seqno: {seqno}, type: {type(seqno)}')
    
    # get shards
    payload = {'id': '1', 'jsonrpc': '2.0', 'method': 'shards', 'params': {'seqno': seqno}}
    async with session.post(url=str(settings.ton_http_api.url), json=payload) as res:
        data = await res.json()
        if res.status != 200:
            raise RuntimeError(f'Failed with code {res.status}: {data}')
        logger.info(f'Result: {data}')
        num_shards = len(data['result'])
    
    return {}


async def metrics_task(settings: Settings):
    headers = None
    if settings.ton_http_api.api_token:
        headers = {'X-API-Key': settings.ton_http_api.api_token}
    
    async with ClientSession(headers=headers) as session:
        shards_data_task = get_shards_data(session, settings=settings)
        shards = await shards_data_task
        # shards, = await asyncio.gather(*[shards_data_task], return_exceptions=False)
    logger.info(f'shards: {shards}')
    return
