from fastapi import Depends

from backend.core.db import get_client
from backend.core.settings import Settings


# settings
class SettingsDep:
    def __init__(self):
        self.settings = None
    
    def __call__(self, *args, **kwargs):
        if self.settings is None:
            self.settings = Settings()
        return self.settings

settings_dep = SettingsDep()


# clickhouse
def db_dep(settings: Settings = Depends(settings_dep)):
    client = get_client(settings.database)
    return client
