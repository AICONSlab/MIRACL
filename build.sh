#!/bin/bash

if [ -x "$(command -v docker)" ]; then
	    echo "Docker installation found. Building image."
	    export HOST_USER=$(whoami)
	    # Change user in docker-compose.yml to host user
	    sed -i "s/\(\/home\/\).*\(\/.Xauthority:\/home\/\).*\(\/.Xauthority\)/\1$HOST_USER\2$HOST_USER\3/g" docker-compose.yml
	    docker build \
	    --build-arg USER_ID=$(id -u) \
	    --build-arg GROUP_ID=$(id -g) \
	    --build-arg USER=$HOST_USER \
	    -t mgoubran/miracl .

	else
	    echo "Docker installation not found. Please install Docker first."
fi








