import logging

from datetime import datetime
from typing import List
from fastapi import FastAPI, Query, Depends
from clickhouse_connect.driver import Client

from backend.api import schema
from backend.api.deps import db_dep


# Enable logging
logging.basicConfig(format="[%(asctime)s:%(name)s:%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(docs_url='/')


@app.get('/tps', response_model=List[schema.TpsRecord])
def get_tps(from_datetime: datetime=Query(None, title='From date'),
            to_datetime: datetime=Query(None, title='To date'),
            limit: int=Query(2048, title='Max records in response', ge=0, le=2048),
            sort: str=Query('desc', title='Sort order', enum=['asc', 'desc']),
            db: Client=Depends(db_dep)):
    logger.info('1')
    query = 'select * from tps.history'
    where_clause = []
    if from_datetime is not None:
        where_clause.append(f"timestamp >= {from_datetime}")
    if to_datetime is not None:
        where_clause.append(f"timestamp <= {to_datetime}")
    if where_clause:
        where_clause = ' and '.join(*where_clause)
        query += ' ' + where_clause
    query += f' order by seqno {sort}'
    query += f' limit {limit}'
    logger.info(f'Query: {query}')
    res = db.query(query)
    
    result = []
    for x in res.named_results():
        result.append(schema.TpsRecord(**x))
    return result
