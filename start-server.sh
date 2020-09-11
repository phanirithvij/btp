#!/bin/bash

# python -m venv venv
source venv/bin/activate
pwd
echo -n "Using "
which pip; pip -V
# pip install -r server/requirements.new.txt

if ! [ -x "$(command -v redis-server)" ]; then
    echo 'Warning: redis is not installed or is not in the $PATH.' >&2
    if [ -f "/etc/arch-release" ]; then
	sudo pacman -S redis
    else
    	curl -O http://download.redis.io/redis-stable.tar.gz
    	tar xvzf redis-stable.tar.gz
    	rm redis-stable.tar.gz
    	cd redis-stable
    	make -j8
    fi 
fi

echo -e "\n\n\n -------------------------------------"
if [ -x "$(command -v konsole)" ]; then
    { konsole -e ./run-redis.sh; } &
    { konsole -e ./run-celery.sh; } &
    { konsole -e bash -c "source venv/bin/activate && python -m server"; } &
elif [ -x "$(command -v x-terminal-emulator)" ]; then
    x-terminal-emulator -e ./run-redis.sh &
    x-terminal-emulator -e ./run-celery.sh &
    python -m server
else
    echo "Please add your terminal emulator in the else block of the start-server.sh script"
fi
