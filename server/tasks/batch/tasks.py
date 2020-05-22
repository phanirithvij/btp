import shutil

from server.tasks import ProgressTask, celery, logger
from pathlib import Path
from time import time


@celery.task(bind=True, base=ProgressTask)
def zip_files(
        self,
        output_filename: str,
        dir_name: str,
        update_url: str):
    # assigned id for this task
    # print(self.request.id)

    outfile = Path(output_filename)
    # if a dir is sent assign the out file a timestamp name
    if outfile.is_dir():
        outfile = outfile / f"{time()}"
    self.configure(update_url)

    logger.info("Started Zipping")
    progress = {'status': 'started', 'taskid': self.request.id}
    self.progress = progress

    shutil.make_archive(outfile.resolve(), 'zip', dir_name)

    progress['status'] = 'done'
    progress['filename'] = output_filename
    self.progress = progress
