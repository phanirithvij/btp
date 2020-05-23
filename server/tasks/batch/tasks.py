import os
import subprocess
import zipfile
from pathlib import Path
from time import time
from timeit import default_timer as timer

import requests
from checksumdir import dirhash
from tqdm import gui, tqdm

from server.tasks import ProgressTask, celery, logger


@celery.task(bind=True, base=ProgressTask)
def zip_files(
        self,
        out_filepath: str,
        dir_name: str,
        user_id: str,
        update_url: str):
    # assigned id for this task
    # print(self.request.id)

    start = timer()
    folder_hash = dirhash(dir_name)
    end = timer()
    logger.info("took " + str(end - start) + " secs to compute folder hash")
    logger.info(folder_hash)

    outfile = Path(out_filepath)
    # if a dir is sent assign the out file a timestamp name
    if outfile.is_dir():
        # TODO instead of timestamp get a unique id based on requested content
        # to prevent re zipping
        outfile = outfile / f"{folder_hash}.zip"
    self.configure(update_url)

    logger.info("Started Zipping")
    progress = {
        'status': 'started',
        'taskid': self.request.id,
        'userid': user_id,
        'current': 0
    }
    self.progress = progress

    if outfile.is_file():
        # already exists with same hash
        progress['status'] = 'done'
        progress['filename'] = os.path.basename(outfile)
        self.progress = progress
        return

    # shutil.make_archive(outfile.resolve(), 'zip', dir_name)
    # pwd will be server/..
    # TODO zipfile with tqdm can be used
    # TODO add to existing zip file can also be done
    # faster and better
    # remove the checksumdir
    # use directory access time
    # Works for this because files are being added and deleted

    def zipdir(path, ziph):
        # ziph is zipfile handle
        curr = 0
        total = 0
        for root, dirs, files in tqdm(os.walk(path)):
            for file in files:
                total += 1
        progress['total'] = total
        for root, dirs, files in tqdm(os.walk(path)):
            for file in files:
                curr += 1
                if curr % 10 == 0:
                    progress['current'] = curr
                    self.progress = progress
                ziph.write(os.path.join(root, file))

    with zipfile.ZipFile(str(outfile), 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(dir_name, zipf)

    # out = subprocess.check_output(
    #     ['server/scripts/ziptool', dir_name, str(outfile), user_id, update_url, self.request.id])
    # logger.info(out)

    progress['status'] = 'done'
    progress['filename'] = os.path.basename(outfile)
    self.progress = progress
