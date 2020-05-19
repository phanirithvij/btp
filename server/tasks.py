import json

import requests
from celery import Celery, Task
from celery.utils.log import get_task_logger
from server.config import Config

logger = get_task_logger(__name__)


celery = Celery(__name__, broker=Config.CELERY_BROKER_URL,
                backend=Config.CELERY_RESULT_BACKEND)


class CustomTask(Task):
    """
    A simple task api.
    """

    @property
    def progress(self):
        return self._progress
    # a setter function for progress
    # which sends updates to the initially specified update_url

    def configure(self, update_url: str, user_id: str):
        self.update_url = update_url
        self.user_id = user_id
        self._progress = {'status': 'PENDING', 'userid': user_id}

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.update()

    def update(self):
        assert self.update_url is not None
        r = requests.post(self.update_url, json=self._progress)
        if r.status_code != 200:
            logger.warn(msg=' '.join(
                [f"Response for {self.update_url}",
                 f"was {r.status_code} != 200"]))


@celery.task(bind=True, base=CustomTask)
def process_image(
        self,
        filename: str,
        file: str,
        jsonfile_path: str,
        user_id: str,
        element_id: str,
        update_url: str):

    # assigned id for this task
    # print(self.request.id)
    logger.info("Works")
