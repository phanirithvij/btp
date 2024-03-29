import requests
from celery import Celery, Task
from celery.utils.log import get_task_logger
from dotenv import find_dotenv, load_dotenv

from server.config import Config

logger = get_task_logger(__name__)


load_dotenv(find_dotenv(), verbose=True)


#
# https://github.com/celery/celery/issues/2570
# celery tasks in different files is pain
#
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL,
                backend=Config.CELERY_RESULT_BACKEND)

celery.autodiscover_tasks(['server.tasks_split.save'])


class ProgressTask(Task):
    """
    A simple task api with progress update support.
    Send a local request and use socketio to update to the client.
    """

    @property
    def progress(self):
        return self._progress
    # a setter function for progress
    # which sends updates to the initially specified update_url

    def configure(self, update_url: str, assert__if_no_progress=False):
        self.update_url = update_url
        self.assert__if_no_progress = assert__if_no_progress
        self._progress = {'status': 'PENDING'}

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.update()

    def update(self):
        if self.assert__if_no_progress:
            assert self.update_url is not None

        if self.update_url is not None:
            r = requests.post(self.update_url, json=self._progress)
            logger.info('Sending updates for task ' + self._progress['taskid'])
            if r.status_code != 200:
                logger.warn(msg=' '.join(
                    [f"Response for {self.update_url}",
                     f"was {r.status_code} != 200"]))
        else:
            logger.warn('WARING: progress_url was none for a task')
