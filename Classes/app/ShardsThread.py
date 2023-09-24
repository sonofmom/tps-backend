from Classes.TonHttpApi import TonHttpApi
from threading import Thread
import time
import random

class ShardsThread(Thread):
    def __init__(self, id, config, log=None, queue=None, gk=None, max_rps=1):
        Thread.__init__(self)
        self.id = id
        self.config = config
        self.log = log
        self.queue = queue
        self.gk = gk
        self.min_runtime_ms = (1 / max_rps) * 1000
        self.api = TonHttpApi(self.config["http-api"],self.log)

    def run(self):

        dummy_result = 1
        while True:
            if self.gk.kill_now:
                self.log.log(self.__class__.__name__, 3, '[{}] Terminating'.format(self.id))
                return

            start_timestamp = time.time()

            rs = self.api.jsonrpc("getMasterchainInfo", {})
            seqno = rs["result"]["last"]["seqno"]

            params = {
                "seqno": seqno
            }
            self.log.log(self.__class__.__name__, 3, '[{}] Requesting shards for seqno {}'.format(self.id,params["seqno"]))
            rs = None
            try:
                rs = self.api.jsonrpc("shards", params)
            except Exception as e:
                self.log.log(self.__class__.__name__, 1, "Query failure: {}".format(str(e)))

            runtime_ms = (time.time() - start_timestamp) * 1000
            if not rs:
                self.log.log(self.__class__.__name__, 3, '[{}] Query failed in {} ms'.format(self.id,runtime_ms))
            elif rs["ok"]:
                result = len(rs['result']['shards'])

                # FAKE GENERATOR, REMOVE ME!!!!!!
                #
                dummy_result += random.randint(0,10)
                result = dummy_result

                self.log.log(self.__class__.__name__, 3, '[{}] Query completed in {} ms with result {} shards'.format(self.id,runtime_ms, result))
                self.queue.put([int(time.time()), result])
            else:
                self.log.log(self.__class__.__name__, 3, '[{}] Query failed in {} ms'.format(self.id,runtime_ms))

            if (runtime_ms < self.min_runtime_ms):
                sleep_ms = int(self.min_runtime_ms - runtime_ms)
                self.log.log(self.__class__.__name__, 3, '[{}] Sleeping for {} ms'.format(self.id,sleep_ms))
                time.sleep(sleep_ms/1000)

# end class
