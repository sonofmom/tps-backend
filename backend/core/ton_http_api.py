import backend.utils.general as gt


class TonHttpApi:
    def __init__(self, config, log=None):
        self.config = config
        self.log = log

    def query(self, payload):
        headers = None
        if "api_token" in self.config and self.config["api_token"]:
            headers = {"X-API-Key": self.config["api_token"]}

        try:
            result = gt.send_api_query(
                self.config["url"],
                payload=payload,
                headers=headers,
                method='post')
        except Exception as e:
            raise Exception("Query failed: {}".format(str(e)))

        return result

    def jsonrpc(self, method, params={}):
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 1
        }
        return self.query(payload)


    def get_pool_nominators(self, address):
        params = {
            "address": address,
            "method": 'list_nominators',
            "stack": []
        }
        result = self.jsonrpc("runGetMethod", params)

    def get_pool_data(self, address):
        params = {
            "address": address,
            "method": 'get_pool_data',
            "stack": []
        }
        result = self.jsonrpc("runGetMethod", params)

    def lookup_mc_block(self, seqno=None, timestamp=None, as_string=False):
        if timestamp and isinstance(timestamp, float):
            timestamp = int(timestamp)

        params = {
            'workchain': -1,
            'shard': 8000000000000000
        }
        if seqno:
            params['seqno'] = seqno
        elif timestamp:
            params['unixtime'] = timestamp

        try:
            rs = self.jsonrpc('lookupBlock', params=params)
            if not as_string:
                return rs['result']
            else:
                return "({},{},{}):{}:{}".format(
                    params['workchain'],
                    params['shard'],
                    rs['result']['seqno'],
                    gt.b64_to_hex(rs['result']['root_hash']),
                    gt.b64_to_hex(rs['result']['file_hash'])
                ).upper()

        except Exception as e:
            return None
# end class
