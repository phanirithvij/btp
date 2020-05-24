import os
import subprocess
import zipfile
import zlib
from pathlib import Path
from time import time
from timeit import default_timer as timer

import requests
from flask_caching import Cache
from tqdm import gui, tqdm

import server
from server.tasks import ProgressTask, celery, logger


def dir_id(dirpath: str) -> str:
    """
    Dir id will be different only if some file is added
    """
    res = os.stat(dirpath)
    atime = res.st_atime
    mtime = res.st_mtime
    ctime = res.st_ctime
    return zlib.adler32(f"{atime}{mtime}{ctime}".encode('utf8'))


@celery.task(bind=True, base=ProgressTask)
def zip_files(
        self,
        out_filepath: str,
        dir_name: str,
        username: str,
        user_id: str,
        update_url: str):
    # assigned id for this task
    # print(self.request.id)
    with server.app.app_context():
        print(server.cache.get('pokepoke'))
        # session['running_tasks'][username] = self.request.id


    folder_id = f"{username}_{dir_id(dir_name)}"

    outfile = Path(out_filepath)
    # if a dir is sent assign the out file a timestamp name
    if outfile.is_dir():
        # TODO instead of timestamp get a unique id based on requested content
        # to prevent re zipping
        outfile = outfile / f"{folder_id}.zip"
    self.configure(update_url)

    logger.info("Started Zipping")
    progress = {
        'status': 'started',
        'taskid': self.request.id,
        'userid': user_id,
        'username': username,
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
        for root, dirs, files in os.walk(path):
            for file in files:
                total += 1
        progress['total'] = total
        # TODO tqdm not showing
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

    with server.app.app_context():
        # del session['running_tasks'][username]
        print(server.cache.delete('pokepoke'))
