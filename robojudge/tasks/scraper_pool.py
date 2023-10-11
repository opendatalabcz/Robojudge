import signal
import os
import asyncio

from multiprocessing import Queue, Process

from robojudge.components.paginating_scraper import PaginatingScraper
from robojudge.utils.logger import logging

WORKER_PROCESS_COUNT = 5

FINISH_WORD = "DONE"

logger = logging.getLogger(__name__)

# TODO: refactor into static functions?


class FetchCasesWorkerPool:
    queue: Queue
    worker_pids: list[int] = []

    def __init__(self) -> None:
        self.queue = Queue()
        # Gets "inherited" by the worker processes
        signal.signal(signal.SIGINT, self.shut_down_pool)
        signal.signal(signal.SIGTERM, self.shut_down_pool)

        logger.info(f"Initializing {WORKER_PROCESS_COUNT} fetch worker processes.")
        for index in range(WORKER_PROCESS_COUNT):
            parser = Process(target=FetchCasesWorker.run, args=(self.queue, index))
            parser.start()
            self.worker_pids.append(parser.pid)

    def shut_down_pool(self, *args):
        logger.info(f"Terminating fetch worker processes based on signal.")
        self.queue.put(FINISH_WORD)


class FetchCasesWorker:
    @staticmethod
    def run(q: Queue, worker_id: int):
        while True:
            try:
                fetch_job = q.get()

                if fetch_job == FINISH_WORD:
                    q.put(FINISH_WORD)
                    break

                logger.info(f"Initializing a fetch job in worker process '{worker_id}'.")
                asyncio.run(
                    PaginatingScraper.run_fetch_job(
                        token=fetch_job["token"], request=fetch_job["request"]
                    )
                )

            except Exception:
                logger.exception(
                    f"Fetching worker #{worker_id} - unexpected error:"
                )


pool = FetchCasesWorkerPool()
