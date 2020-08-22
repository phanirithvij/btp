#!/bin/bash

#pip install virtualenv && virtualenv venv
source venv/bin/activate
pwd
pip install -r server/requirements.txt

if ! [ -x "$(command -v redis-server)" ]; then
    echo 'Warning: redis is not installed or is not in the $PATH.' >&2
    curl -O http://download.redis.io/redis-stable.tar.gz
    tar xvzf redis-stable.tar.gz
    rm redis-stable.tar.gz
    cd redis-stable
    make -j8
fi

echo -e "\n\n\n -------------------------------------"
{ konsole -e ./run-redis.sh; } &
{ konsole -e ./run-celery.sh; } &
{ konsole -e bash -c "source venv/bin/activate && python -m server"; } &

