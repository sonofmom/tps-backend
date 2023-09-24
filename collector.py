#!/usr/bin/env python3
#

import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import Libraries.tools.general as gt
import time
from psycopg.rows import dict_row
from Classes.AppConfig import AppConfig
from Classes.app.ShardsThread import ShardsThread
from Classes.app.TpsThread import TpsThread
from queue import Queue

def run():
    description = 'Read overlays data created by node(s) and updates database.'
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                    description = description)

    parser.add_argument('-c', '--config',
                        required=True,
                        dest='config_file',
                        action='store',
                        help='Script configuration file - REQUIRED')

    parser.add_argument('-v', '--verbosity',
                        required=False,
                        type=int,
                        default=0,
                        dest='verbosity',
                        action='store',
                        help='Verbosity 0 - 3 - OPTIONAL, default: 0')

    cfg = AppConfig(parser.parse_args())

    dbc = cfg.db_rw.cursor(row_factory=dict_row)

    queues = {
        'shards': Queue(),
        'tps': Queue()
    }
    th_db = []
    th_db.append(
        ShardsThread(
            id = 'T1',
            config=cfg.config,
            log=cfg.log,
            gk=cfg.GracefulKiller,
            queue=queues['shards'],
            max_rps=cfg.config['limits']['shards_rps']
        )
    )
    th_db.append(
        TpsThread(
            id = 'T1',
            config=cfg.config,
            log=cfg.log,
            gk=cfg.GracefulKiller,
            queue=queues['tps'],
            params=cfg.config['tps'],
            max_rps=cfg.config['limits']['tps_rps']
        )
    )

    for element in th_db:
        element.start()

    while True:
        if cfg.GracefulKiller.kill_now:
            cfg.log.log(os.path.basename(__file__), 3, "Exiting main loop")
            break

        if queues['shards'].qsize():
            cfg.log.log(os.path.basename(__file__), 3, "Processing {} shard queue entries".format(queues['shards'].qsize()))
            for idx in range(queues['shards'].qsize()):
                result = queues['shards'].get()

                sql = """INSERT INTO shards (
                            record_timestamp,
                            value
                            )
                            VALUES (%s,%s) RETURNING *;
                """

                dbc.execute(sql, (
                    gt.get_datetime_utc(timestamp=result[0], return_none=True),
                    result[1],))

        if queues['tps'].qsize():
            cfg.log.log(os.path.basename(__file__), 3, "Processing {} tps queue entries".format(queues['tps'].qsize()))
            for idx in range(queues['tps'].qsize()):
                result = queues['tps'].get()

                sql = """INSERT INTO tps (
                            record_timestamp,
                            value
                            )
                            VALUES (%s,%s) RETURNING *;
                """

                dbc.execute(sql, (
                    gt.get_datetime_utc(timestamp=result[0], return_none=True),
                    result[1],))

        cfg.db_rw.commit()
        time.sleep(1)

    sys.exit(0)

if __name__ == '__main__':
    run()
