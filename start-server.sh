#!/bin/bash

# pip install virtualenv && virtualenv venv
# virtualenv venv
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

# # download go if not exists
# if ! [ -x "$(command -v go)" ]; then
#     wget -q -O - https://raw.githubusercontent.com/canha/golang-tools-install-script/master/goinstall.sh | bash
#     source ~/.bashrc
#     if ! [ -x "$(command -v go)" ]; then
#         echo "Go installation failed please install go and try again"
#         exit 1
#     fi
# fi

# cd server/scripts
# go list "github.com/schollz/progressbar" || go get -u -v "github.com/schollz/progressbar"
# make
# cd ../../


echo -e "\n\n\n -------------------------------------"
x-terminal-emulator -e ./run-redis.sh &
x-terminal-emulator -e ./run-celery.sh &
python -m server
