import os
import subprocess
import zipfile
import zlib
from pathlib import Path
from time import time
from timeit import default_timer as timer

import requests
from celery.signals import (celeryd_init, task_failure, task_postrun,
                            task_prerun)
from tqdm import tqdm

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


@celeryd_init.connect
def init_signals(*args, **kwargs):
    # TODO to do something after celery init
    # do it here
    with open('logs/init.log', 'w+') as l:
        print('INIT '*100, file=l)


@task_prerun.connect
def pretask(task_id=None, task=None, *args, **kwargs):
    # If the task is zip_files add it to running_zip_tasks
    if 'zip_files' in str(type(task)):
        with server.app.app_context():
            running = server.cache.get('running_zip_tasks')
            print('-----')
            # print(kwargs, type(kwargs))
            running[task_id] = kwargs['kwargs']
            logger.info(running[task_id])
            server.cache.set('running_zip_tasks', running)


@task_postrun.connect
def postask(task_id=None, task=None, retval=None, state=None, *args, **kwargs):
    # If the task is zip_files remove it from running_zip_tasks
    if 'zip_files' in str(type(task)):
        with server.app.app_context():
            running = server.cache.get('running_zip_tasks')
            logger.info(running[task_id])
            del running[task_id]
            server.cache.set('running_zip_tasks', running)


@task_failure.connect
def failtask(task_id=None, exception=None, *args, **kwargs):
    print('task failed')
    print(task_id, exception, args, kwargs)


@celery.task(bind=True, base=ProgressTask)
def zip_files(
        self,
        out_filepath: str = None,
        dir_name: str = None,
        username: str = None,
        user_id: str = None,
        update_url: str = None):
    # assigned id for this task
    print(self.request.id)
    print('__'*10)
    # with server.app.app_context():
    #     running = server.cache.get('running_zip_tasks')
    #     running[self.request.id] = {'username': username, 'user_id': user_id}
    #     server.cache.set('running_zip_tasks', running)

    folder_id = f"{username}_{dir_id(dir_name)}"

    outfile = Path(out_filepath)
    # if a dir is sent assign the out file a timestamp name
    if outfile.is_dir():
        # instead of timestamp get a unique id based on requested content
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
