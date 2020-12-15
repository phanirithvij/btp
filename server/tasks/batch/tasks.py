import os
import shutil
import zipfile
import zlib
from pathlib import Path

from celery.signals import (celeryd_init, task_failure, task_postrun,
                            task_prerun)
from tqdm import tqdm

import server
from server.config import Config
from server.db import UserFileSystem
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


def dir_id_from_files(files=[]) -> str:
    return zlib.adler32("_".join(files).encode('utf8'))


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
            # cache cleared by flask
            if running is None:
                server.cache.set('running_zip_tasks', {})
            print('-----')
            print(kwargs, type(kwargs))
            running[task_id] = kwargs['kwargs']
            logger.info(running[task_id])
            server.cache.set('running_zip_tasks', running)


@task_postrun.connect
def postask(task_id=None, task=None, retval=None, state=None, *args, **kwargs):
    # If the task is zip_files remove it from running_zip_tasks
    if 'zip_files' in str(type(task)):
        with server.app.app_context():
            running = server.cache.get('running_zip_tasks')
            # cache cleared by flask so status is lost
            # If task takes too long to execute this happens
            # TODO increase CACHE_DEFAULT_TIMEOUT ?
            if running is None:
                server.cache.set('running_zip_tasks', {})
            else:
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
        update_url: str = None,
        partial: bool = False,
):
    # assigned id for this task
    print(self.request.id)
    print('__'*10)
    # with server.app.app_context():
    #     running = server.cache.get('running_zip_tasks')
    #     running[self.request.id] = {'username': username, 'user_id': user_id}
    #     server.cache.set('running_zip_tasks', running)

    folder_id = f"{username}_{dir_id(dir_name)}"
    if partial:
        folder_id = f"{username}_{dir_id(dir_name)}_p"

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
        'current': 0,
        'type': 'export_task'
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
        print("DIR is", path)
        prev = os.getcwd()
        # print("DIR is", os.getcwd())
        # print("DIR is", os.getcwd())
        # print('PAR IS', Path(path).parent)
        dirname_ = os.path.basename(path)
        os.chdir(Path(path).parent)
        for root, dirs, files in tqdm(os.walk(path)):
            for file in files:
                curr += 1
                if curr % 10 == 0:
                    progress['current'] = curr
                    self.progress = progress
                # print(file, root)
                ziph.write(os.path.join(root, file),
                           arcname=Path(dirname_) / file)
        os.chdir(prev)

    with zipfile.ZipFile(str(outfile), 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(dir_name, zipf)

    # out = subprocess.check_output(
    #     ['server/scripts/ziptool', dir_name, str(outfile), user_id, update_url, self.request.id])
    # logger.info(out)

    progress['status'] = 'done'
    progress['filename'] = os.path.basename(outfile)
    self.progress = progress


@celery.task(bind=True, base=ProgressTask)
def combine_zips(
        self,
        out_filepath: str = None,
        dir_names=[],
        usernames=[],
        user_id: str = None,
        update_url: str = None):

    pass


@celery.task(bind=True, base=ProgressTask)
def delete_zips(self, usernames=[], user_id: str = None, progress_url: str = None):
    progress = {
        'type': 'delete_zip_task',
        'taskid': self.request.id,
        'userid': user_id,
        'status': 'started'
    }
    self.configure(progress_url)
    self.progress = progress
    if user_id is not None:
        logger.warn(f"User {user_id} deleted {usernames}")
    for user in usernames:
        for fi in Path(Config.TEMP_DIR).iterdir():
            if os.path.basename(fi).startswith(user):
                print(f"Delete {fi}")
                os.remove(fi)

    progress['status'] = 'done'
    self.progress = progress


@celery.task(bind=True, base=ProgressTask)
def zip_files_partial(
        self,
        files=[],
        username: str = None,
        user_id: str = None,
        update_url: str = None):

    userfs = UserFileSystem(username)

    dirname = dir_id_from_files(files)
    dirname = Path(Config.TEMP_DIR) / f"{dirname}"

    if dirname.is_dir():
        # already exists
        self.configure(update_url)
        progress = {'status': 'done', 'file': None, 'userid': user_id}
        for f in Path(Config.TEMP_DIR).iterdir():
            name = os.path.basename(f)
            if len(str(name).split('_')) == 3:
                if str(name).split('_')[0] == username:
                    progress['file'] = name
                    break
        if progress['file'] is not None:
            # found a partial zip
            self.progress = progress
            return

    try:
        os.makedirs(dirname)
    except Exception as e:
        print(e)

    for file in files:
        shutil.copy(userfs.user_dir() / file, dirname)

    task = zip_files.apply_async(
        kwargs={
            "out_filepath": Config.TEMP_DIR,
            "dir_name": f'{dirname}',
            "username": username,
            "user_id": user_id,
            "update_url": update_url,
            "partial": True,
        },
        queue="main_queue",
    )
