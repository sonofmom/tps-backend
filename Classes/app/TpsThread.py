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
            "address": "EQBg_ebI0nzsQBRfQ4u9dvemQKApcQLfZqBNVidIwVw2owIH",
            "method": "seqno",
            "stack": []
        }
        self.log.log(self.__class__.__name__, 3, '[{}] initializing process with counter {}'.format(self.id,self.params["rps_counter"]))

        dummy_result = 10000
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
                result = rs['result']['stack']

                # FAKE GENERATOR, REMOVE ME!!!!!!
                #
                dummy_result += random.randint(0,200)
                result = dummy_result

                self.log.log(self.__class__.__name__, 3, '[{}] Query completed in {} ms with result {} tps'.format(self.id,runtime_ms, result))
                self.queue.put([int(time.time()), result])
            else:
                self.log.log(self.__class__.__name__, 3, '[{}] Query failed in {} ms'.format(self.id,runtime_ms))

            if (runtime_ms < self.min_runtime_ms):
                sleep_ms = int(self.min_runtime_ms - runtime_ms)
                self.log.log(self.__class__.__name__, 3, '[{}] Sleeping for {} ms'.format(self.id,sleep_ms))
                time.sleep(sleep_ms/1000)

# end class
