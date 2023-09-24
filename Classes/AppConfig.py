import os
import sys
import json
import Libraries.tools.general as gt
from Classes.Logger import Logger
import psycopg
from Classes.TonHttpApi import TonHttpApi
from Classes.TonIndexer import TonIndexer
import Classes.GracefulKiller as GracefulKiller

class AppConfig:
    def __init__(self, args):
        self.args = args
        self.log = Logger(args.verbosity)
        self.config = None
        self.cache_path = None
        self.db_rw = None
        self.tmp = {}
        self.start_timestamp = gt.get_timestamp()
        self.GracefulKiller = GracefulKiller.GracefulKiller()

        if hasattr(self.args, 'config_file'):
            fn = self.args.config_file
            self.log.log(self.__class__.__name__, 3, 'Config file {}'.format(fn))
            if not gt.check_file_exists(fn):
                self.log.log(self.__class__.__name__, 1, "Configuration file does not exist!")
                sys.exit(1)
            try:
                fh = open(fn, 'r')
                self.config = json.loads(fh.read())
                fh.close()
            except Exception as e:
                self.log.log(self.__class__.__name__, 1, "Configuration file read error: {}".format(str(e)))
                sys.exit(1)

            if "liteClient" in self.config:
                fn = self.config["liteClient"]["config"];
                self.log.log(self.__class__.__name__, 3, 'LS Config file {}'.format(fn))
                if not gt.check_file_exists(fn):
                    self.log.log(self.__class__.__name__, 1, "LS Configuration file does not exist!")
                    sys.exit(1)
                try:
                    fh = open(fn, 'r')
                    self.ls_config = json.loads(fh.read())
                    fh.close()
                except Exception as e:
                    self.log.log(self.__class__.__name__, 1, "LS Configuration file read error: {}".format(str(e)))
                    sys.exit(1)

            if "caches" in self.config:
                self.cache_path = "{}/{}.{}".format(self.config["caches"]["path"],self.config["caches"]["prefix"], os.getuid())
                if not os.path.exists(self.cache_path):
                    os.makedirs(self.cache_path)

                if not (os.path.exists(self.cache_path) and os.path.isdir(self.cache_path) and os.access(self.cache_path, os.W_OK)):
                    self.log.log(self.__class__.__name__, 1, "Cache path {} could not be created or is not writable".format(self.cache_path))
                    sys.exit(1)

            if "database" in self.config:
                if "credentials_ro" in self.config["database"]:
                    self.db_ro = psycopg.connect(
                        host=self.config["database"]["host"],
                        port=self.config["database"]["port"],
                        dbname=self.config["database"]["dbname"],
                        user=self.config["database"]["credentials_ro"]["user"],
                        password=self.config["database"]["credentials_ro"]["password"])

                if "credentials_rw" in self.config["database"]:
                    self.db_rw = psycopg.connect(
                        host=self.config["database"]["host"],
                        port=self.config["database"]["port"],
                        dbname=self.config["database"]["dbname"],
                        user=self.config["database"]["credentials_rw"]["user"],
                        password=self.config["database"]["credentials_rw"]["password"])

            if "http-api" in self.config:
                self.http_api = TonHttpApi(self.config["http-api"], self.log)

            if "indexer" in self.config:
                self.indexer = TonIndexer(self.config["indexer"], self.log)

# end class
