#!/bin/bash

# Check if Docker is installed
if [ -x "$(command -v docker)" ]; then
	    echo
	    echo "Docker installation found. Building image."
	    echo
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

	        build_status_code=$?
		if [ $build_status_code -eq 0 ]; then
			echo
			echo "Build was successfull! Checking docker-compose installation."
			echo

			# Test if docker-compose is installed
			if [ -x "$(command -v docker-compose)" ]; then
				echo "docker-compose installation found. Run 'docker-compose up -d' to start the MIRACL container in background."
				echo
			else
				echo "docker-compose installation not found. Please install docker-compose to run the MIRACL container."
				echo
			fi
		else
			echo
			echo "Build not successfull! An error occured with exit code: $build_status_code"
			echo
		fi

	else
	    echo
	    di_status_code=$?
	    echo "Docker installation not found. Please install Docker first."
	    echo "Exiting with status code $di_status_code"
	    echo
fi








