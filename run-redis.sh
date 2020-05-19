#!/bin/bash
if ! [ -x "$(command -v redis-server)" ]; then
    echo 'Warning: redis is not installed or is not in the $PATH.' >&2
    curl -O http://download.redis.io/redis-stable.tar.gz
    tar xvzf redis-stable.tar.gz
    rm redis-stable.tar.gz
    cd redis-stable
    make -j8
    src/redis-server
else
    # check if redis is running
    pong=$(redis-cli ping)
    if [[ "$pong" == "PONG" ]]; then
        # exit
        exit 1
        # echo $pong
    else
        redis-server
    fi
fi
