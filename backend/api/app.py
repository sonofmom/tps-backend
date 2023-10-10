import logging

from fastapi import FastAPI, Query, Depends
from clickhouse_connect.driver import Client

from backend.api.deps import db_dep


logger = logging.getLogger(__name__)
app = FastAPI(docs='/')


@app.get('/tps')
def get_tps(self, 
            from_datetime=Query(None, title='From date'),
            to_datetime=Query(None, title='To date'),
            db: Client=Depends(db_dep)):
    query = 'select * from tps.history'
    where_clause = []
    if from_datetime is not None:
        where_claus.append(f"timestamp >= {from_datetime}")
    if to_datetime is not None:
        where_clause.append(f"timestamp <= {to_datetime}")
    where_clause = ' and '.join(*where_clause)
    if where_clause:
        query += ' ' + where_clause
    logger.info(f'Query: {query}')
    res = db.query(query)
    return res
