#!/bin/bash

new_inst=false
if [ ! -d "venv" ]; then
    echo "Creating python virtual env at ./venv"
    python -m venv venv
    new_inst=true
fi

source venv/bin/activate
pwd
echo -n "Using "
which pip; pip -V

if [ $new_inst == true ]; then
    echo "Installing python requirements"
    pip install -r server/requirements.latest.txt
fi

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
    { konsole -e ./run-celery_split.sh; } &
    # { konsole -e bash -c "source venv/bin/activate && python -m server"; } &
    tries=0
    while true;
    do
        pong=$(redis-cli ping)
        sleep 2
        if [[ "$pong" == "PONG" ]]; then
            # exit
            python -m server
            break
            # echo $pong
        else
            echo "Waiting for redis to come online..."
            tries=$((tries+1))
            if [ $tries -gt 3 ]; then
                echo "Timedout wating for redis"
                break
            fi
        fi
    done

elif [ -x "$(command -v x-terminal-emulator)" ]; then
    x-terminal-emulator -e ./run-redis.sh &
    x-terminal-emulator -e ./run-celery.sh &
    x-terminal-emulator -e ./run-celery_split.sh &
    python -m server
else
    echo "Please add your terminal emulator in the else block of the start-server.sh script"
fi
