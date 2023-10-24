from fastapi import Depends
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery

from backend.core.db import get_client
from backend.core.settings import Settings


# settings
class SettingsDep:
    def __init__(self):
        self.settings = None
    
    def __call__(self):
        if self.settings is None:
            self.settings = Settings()
        return self.settings

settings_dep = SettingsDep()


# clickhouse
def db_dep(settings: Settings = Depends(settings_dep)):
    client = get_client(settings.database)
    return client


# empty api key dependency for openapi schema
def api_key_dep(api_key_header: APIKeyHeader=Depends(APIKeyHeader(name='X-API-Key', auto_error=False)),
                api_key_query: APIKeyQuery=Depends(APIKeyQuery(name='api_key', auto_error=False))):
    pass
