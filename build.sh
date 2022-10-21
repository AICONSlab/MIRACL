#!/bin/bash

# Check if Docker is installed
if [ -x "$(command -v docker)" ]; then
	    echo "Docker installation found. Building image."
	    export HOST_USER=$(whoami)
	    # Change user in docker-compose.yml to host user
	    sed -i "s/\(\/home\/\).*\(\/.Xauthority:\/home\/\).*\(\/.Xauthority\)/\1$HOST_USER\2$HOST_USER\3/g" docker-compose.yml
	    # Build MIRACL image from Dockerfile
	    # Provide whoami, UID and GID
	    docker build \
	    --build-arg USER_ID=$(id -u) \
	    --build-arg GROUP_ID=$(id -g) \
	    --build-arg USER=$HOST_USER \
	    -t mgoubran/miracl .
	
	    	# Test if docker-compose is installed
		if [ -x "$(command -v docker-compose)" ]; then
			echo "Run 'docker-compose up -d' to start the MIRACL container in background."
		else
			echo "docker-compose installation not found. Please install docker-compose to run the MIRACL container."
		fi

	else
	    echo "Docker installation not found. Please install Docker first."
fi








