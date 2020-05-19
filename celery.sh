#!/bin/bash
echo $*
logfile=$1
source venv/bin/activate
pip freeze > pipfreeze
celery -E -A server.tasks worker --loglevel=info -f logfile
