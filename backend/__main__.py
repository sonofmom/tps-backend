#!/usr/bin/env python3
import asyncio
import argparse
import logging

from backend.core.tasks import metrics_task
from backend.core.db import create_tables, get_client
from backend.core.settings import Settings


# Enable logging
logging.basicConfig(format="[%(asctime)s:%(name)s:%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    loop = asyncio.get_running_loop()
    settings = Settings()
    logger.info(f'Settings: {settings}')

    # prepare worker
    create_tables(get_client(settings.database))

    # run loop
    prev_record = None
    while True:
        prev_record = await metrics_task(settings, prev_record=prev_record)
    try:
        while True:
            await metrics_task(settings)
    except asyncio.CancelledError:
        logger.info('Canceled')
    except Exception as ee:
        logger.info(f'Failed: {ee}')
    except KeyboardInterrupt:
        logger.info(f'Interrupted')
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser('tps-worker')
    parser.add_argument('-v', '--verbosity',
                        required=False,
                        type=int,
                        default=0,
                        dest='verbosity',
                        action='store',
                        help='Verbosity 0 - 3 - OPTIONAL, default: 0')
    args = parser.parse_args()
    logger.setLevel({
        0: logging.CRITICAL,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG
    }[args.verbosity])
    asyncio.run(main())
