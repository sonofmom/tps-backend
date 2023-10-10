from datetime import datetime
from pydantic import BaseModel


class TpsRecord(BaseModel):
    seqno: int
    gen_utime: int
    timestamp: datetime
    shard_count: int
    tx_count: int
    gen_utime_delta: int
    tx_count_delta: int
