import subprocess

from server.tasks import ProgressTask, celery, logger
from pathlib import Path
from time import time
import os

@celery.task(bind=True, base=ProgressTask)
def zip_files(
        self,
        out_filepath: str,
        dir_name: str,
        user_id: str,
        update_url: str):
    # assigned id for this task
    # print(self.request.id)

    outfile = Path(out_filepath)
    # if a dir is sent assign the out file a timestamp name
    if outfile.is_dir():
        # TODO instead of timestamp get a unique id based on requested content
        # to prevent re zipping
        outfile = outfile / f"{time()}.zip"
    self.configure(update_url)

    logger.info("Started Zipping")
    progress = {'status': 'started', 'taskid': self.request.id, 'userid': user_id}
    self.progress = progress

    # shutil.make_archive(outfile.resolve(), 'zip', dir_name)
    # pwd will be server/..
    out = subprocess.check_output(['server/scripts/ziptool', dir_name, str(outfile), user_id, update_url, self.request.id])
    logger.info(out)

    progress['status'] = 'done'
    progress['filename'] = os.path.basename(outfile)
    self.progress = progress
