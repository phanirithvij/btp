"""
Usage use with ./run-celery.sh

"""

import os
import signal
import subprocess
from datetime import datetime
from pathlib import Path
from shutil import copyfile

logfile = 'logs/latest-split.log'

LOG_FILES_LIMIT = 10

print('[scripts/celery.py] Restarted Celery')
print(f'[scripts/celery.py] Logging to {logfile}')
# print('[scripts/celery.py] disk_usage', disk_usage(Path('logs/')))

# TODO remove empty logs

filelist = os.listdir('logs')
# print(filelist)
if len(filelist) > LOG_FILES_LIMIT:
    last_removed = None
    for f in filelist[LOG_FILES_LIMIT:]:
        print(f)
        if 'latest' not in f:
            os.remove('logs/'+f)
            print(f)
    filelist = os.listdir('logs')
    last_removed = filelist[1]
    print("Removed files older than", last_removed)

Path(logfile).touch()
assert Path(logfile).is_file()

with open(logfile, 'w'):
    pass


# command_args = ['./celery.sh', logfile]
# celery -E -A server.tasks worker --loglevel=info -f logfile

# https://stackoverflow.com/a/26021940/8608146
# need to point to the celery object
# 
command_args = [
    'celery', '-E', '-A', 'server.tasks_split.celery', 'worker', '--loglevel=info', '--concurrency=1', '-f', logfile, '-Q', 'split_queue'
]
proc = subprocess.Popen(command_args, shell=False)

try:
    proc.communicate()
except KeyboardInterrupt:
    proc.send_signal(signal.SIGTERM)
    time = datetime.now()
    # rename the log file
    if os.path.exists(logfile):
        copyfile(logfile, f"logs/log{time}.log")
    exit(0)
