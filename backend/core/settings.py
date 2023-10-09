import os
import sys
import json

from typing import Optional
from pydantic import (
    HttpUrl,
    PostgresDsn,
    Field
)

from typing_extensions import Annotated, TypeAlias

from pydantic_core import MultiHostUrl
from pydantic.networks import UrlConstraints
from pydantic_settings import BaseSettings, SettingsConfigDict


ClickhouseDsn = Annotated[
    MultiHostUrl,
    UrlConstraints(host_required=True, allowed_schemes=['clickhouse'])
]



class TonHttpApiSettings(BaseSettings):
    url: HttpUrl = Field()
    api_token: str = Field("")


class DatabaseSettings(BaseSettings):
    # pg_dsn: Optional[PostgresDsn]
    clickhouse_dsn: Optional[ClickhouseDsn]


class TpsSettings(BaseSettings):
    counter_address: str = Field()
    rps: float = Field(0.1)


class ShardsSettings(BaseSettings):
    rps: float = Field(0.1)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='app__',
                                      env_nested_delimiter='__',
                                      env_file=('.env',))

    ton_http_api: TonHttpApiSettings
    database: DatabaseSettings
    tps: TpsSettings
    shards: ShardsSettings

    