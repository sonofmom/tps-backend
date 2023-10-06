from Classes.TonHttpApi import TonHttpApi
from threading import Thread
import time
import random

class TpsThread(Thread):
    def __init__(self, id, config, log=None, queue=None, gk=None, params=None, max_rps=1):
        Thread.__init__(self)
        self.id = id
        self.config = config
        self.log = log
        self.queue = queue
        self.gk = gk
        self.params = params
        self.min_runtime_ms = (1 / max_rps) * 1000
        self.api = TonHttpApi(self.config["http-api"],self.log)

    def run(self):
        params={
            "address": self.params["rps_counter"],
            "method": "get_counter",
            "stack": []
        }
        self.log.log(self.__class__.__name__, 3, '[{}] initializing process with counter {}'.format(self.id,self.params["rps_counter"]))

        last_result = None
        last_ts = None
        while True:
            if self.gk.kill_now:
                self.log.log(self.__class__.__name__, 3, '[{}] Terminating'.format(self.id))
                return

            start_timestamp = time.time()
            self.log.log(self.__class__.__name__, 3, '[{}] Query counter'.format(self.id))

            rs = None
            try:
                rs = self.api.jsonrpc("runGetMethod", params)
            except Exception as e:
                self.log.log(self.__class__.__name__, 1, "Query failure: {}".format(str(e)))

            runtime_ms = (time.time() - start_timestamp) * 1000
            if not rs:
                self.log.log(self.__class__.__name__, 3, '[{}] Query failed in {} ms'.format(self.id,runtime_ms))
            elif rs["ok"]:
                result = int(rs['result']['stack'][0][1],0)
                self.log.log(self.__class__.__name__, 3, '[{}] Query completed in {} ms with result {} tps'.format(self.id,runtime_ms, result))

                if last_result is not None:
                    self.queue.put([int(time.time()), int((result-last_result)/time.time()-last_ts)])

                last_result = result
                last_ts = time.time()
            else:
                self.log.log(self.__class__.__name__, 3, '[{}] Query failed in {} ms'.format(self.id,runtime_ms))

            if (runtime_ms < self.min_runtime_ms):
                sleep_ms = int(self.min_runtime_ms - runtime_ms)
                self.log.log(self.__class__.__name__, 3, '[{}] Sleeping for {} ms'.format(self.id,sleep_ms))
                time.sleep(sleep_ms/1000)

# end class
