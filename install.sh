#!/usr/bin/env bash

# Build MIRACL Docker image with user information from host system

# - Checks if Docker and Docker Compose are installed
# - Dynamically adds and removes user information to
#   prevent errors in Singularity container creation
# - Container user is the same as host user to prevent
#   X11 issues with miraclGUI
# - Checks if script is run with 'sudo'

# Current maintainer of script: Jonas Osmann @ github.com/jono3030
# MIRACL (C) Maged Groubran @ maged.goubran@utoronto.ca

#############
# VARIABLES #
#############

# Enforce strict error handling
set -euo pipefail

function check_for_sudo() {
  SUDO_USER_CHECK=${SUDO_USER:-$USER}

  if [ "$(id -u)" -eq 0 ]; then
    printf "\nError: This script will not work with 'sudo'. Please run it without 'sudo', as the user on your host system (%s) who will be using MIRACL.\n\nInfo: In case you are using 'sudo' because docker requires 'sudo' privileges, create a 'docker' group and add your host user to it. This should allow you to use Docker without 'sudo'.\n\nInfo: For more information on how to create a 'docker' group and add your host user, visit the official Docker docs: https://docs.docker.com/engine/install/linux-postinstall/\n\n" "${SUDO_USER_CHECK}"
    exit 1
  fi
}

function initialize_variables() {
  # Set variables base state
  # Detect OS (Linux/MacOs)
  os=$(uname -s)

  # Script version
  version="2.0.1-beta"

  # Service name
  service_name="miracl"

  # Set default image name
  image_name="aicons/miracl"

  # Set default container name
  container_name="miracl"

  # Set default image version
  miracl_version="latest"

  # Version file version
  miracl_version_file=$(cat ./miracl/version.txt)

  # Set container memory size limit
  if [[ "$os" == "Linux" ]]; then
    shm_mem=$(grep MemTotal /proc/meminfo | awk '{printf "%dmb", int($2/1024*0.85)}')
  elif [[ "$os" == "Darwin" ]]; then
    shm_mem=$(sysctl hw.memsize | awk '{printf "%dmb", int($2/1024/1024*0.85)}')
  else
    echo "Unsupported operating system: $os"
    exit 1
  fi

  # Set array to capture volumes
  volumes=()

  # Base usage
  base_usage="Usage: ./$(basename "$0") [-n service_name] [-i image_name] [-c container_name] [-t {auto, x.x.x}] [-g] [-e] [-v vol:vol] [-l] [-s] [-m] [-h]"
}

##########
# PARSER #
##########

function usage() {

  cat <<help_menu

 $base_usage

   Automatically build MIRACL Docker image with pseudo host user

 Options:

   -n, name of the Docker service (default: 'miracl')
   -i, specify image name (default: 'aicons/miracl')
   -c, specify container name (default: 'miracl')
   -t, set when using specific MIRACL tag/version. Use 'auto' to parse from 'miracl/version.txt' or specify version as floating point value in format 'x.x.x' (default: 'latest')
   -g, enable Nvidia GPU passthrough mode for Docker container which is required for some of MIRACL's scripts e.g. ACE segmentation (default: false)
   -e, disable mounting MIRACL's script directory into Docker container. Mounting is useful if you want host changes to propagate to the container directly (default: enabled)
   -d, set shared memory (shm) size (e.g. '1024mb', '16gb' or '512gb') which is important for e.g ACE (default: int(MemTotal/1024)*0.85 of host machine)
   -v, mount volumes for MIRACL in docker-compose.yml, using a separate flag for each additional volume (format: '/path/on/host:/path/in/container'; default: none)
   -l, write logfile of build process to 'build.log' in MIRACL root directory (default: false)
   -s, print version of build script and exit
   -m, print version of MIRACL on current Git branch and exit
   -h, print this help menu and exit

 Script version: $version
 MIRACL version: $miracl_version_file

help_menu

}

function parse_args() {
  # Parse command line arguments
  while getopts ":n:i:c:t:ged:v:lsmh" opt; do
    case ${opt} in

    n)
      if [ "${OPTARG}" != "$service_name" ]; then
        service_name=${OPTARG}
      fi
      ;;

    i)
      if [ "${OPTARG}" != "$image_name" ]; then
        image_name=${OPTARG}
      fi
      ;;

    c)
      if [ "${OPTARG}" != "$container_name" ]; then
        container_name=${OPTARG}
      fi
      ;;

    t)
      if [[ "${OPTARG}" == "auto" ]]; then
        miracl_version=$miracl_version_file
      elif [[ "${OPTARG}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        miracl_version=${OPTARG}
      else
        echo 'Error: Version input is not a floating point number (format: x.x.x), "auto" or "latest"'
        exit 1
      fi
      ;;

    g)
      gpu=true
      ;;

    e)
      dev=false
      ;;

    d)
      if [ "${OPTARG}" != "$shm_mem" ]; then
        shm_mem=${OPTARG}
      fi
      ;;

    v)
      volumes+=("$OPTARG")
      ;;

    l)
      write_log=true
      ;;

    s)
      echo -e "v$version"
      exit 0
      ;;

    m)
      echo -e "v$miracl_version_file"
      exit 0
      ;;

    h)
      usage
      exit 0
      ;;

    \?)
      echo "Invalid option: -$OPTARG" 1>&2
      printf "\n%s\n" "$base_usage"
      exit 1
      ;;

    :)
      echo "Option -$OPTARG requires an argument." 1>&2
      printf "\n%s\n" "$base_usage"
      exit 1
      ;;

    esac
  done
  shift "$((OPTIND - 1))"
}

##################
# DOCKER COMPOSE #
##################

function populate_docker_compose() {
  # Generate docker-compose.yml file
  cat >docker-compose.yml <<EOF
version: "3.3"
services:
  $service_name:
    image: $image_name:$miracl_version
    tty: true
    environment:
      - DISPLAY
    stdin_open: true
    network_mode: host
    container_name: $container_name
    shm_size: ${shm_mem}
EOF

  if [[ $gpu ]]; then

    cat >>docker-compose.yml <<EOF
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
EOF

  fi

  # Append required volumes
  cat >>docker-compose.yml <<EOF
    volumes:
      - /home/josmann/.Xauthority:/home/josmann/.Xauthority
EOF

  # Append MIRACL scripts folder mounting
  if [[ -z $dev ]]; then

    install_script_dir=$(dirname "$(readlink -f "$0")")

    cat >>docker-compose.yml <<EOF
      - ${install_script_dir}/miracl:/code/miracl
EOF

  fi

  # Add additional volumes
  for v in "${volumes[@]}"; do
    echo "      - $v" >>docker-compose.yml
  done
}

##############
# DOCKERFILE #
##############

# Function to remove user text in Dockerfile if it is already present
function rm_USER_TEXT() {
  sed -i '/STARTUNCOMMENT/,/STOPUNCOMMENT/{//!d}' Dockerfile
}

function populate_dockerfile() {
  # Information that needs to be added to Dockerfile
  # to create pseudo host user. This is required to
  # make X11 work correclty with miraclGUI
  USER_TEXT=$(
    cat <<END
# Setup host user as container user\n\
ARG USER_ID=\$USER_ID\n\
ARG GROUP_ID=\$GROUP_ID\n\
ARG USER=\$USER\n\n\
RUN addgroup --gid \$GROUP_ID \$USER\n\
RUN adduser --disabled-password --gecos '' --uid \$USER_ID --gid \$GROUP_ID \$USER\n\n\
# Change owner of /code directory\n\
RUN chown -R \$USER:\$USER /code\n\
# Change to \$USER\n\
USER \$USER\n\
WORKDIR /home/\$USER
END
  )

  # Check if $USER_TEXT strings are already present and delete if true
  if [ "$(sed -n '/#STARTUNCOMMENT#/{n;p;}' Dockerfile)" != "#STOPUNCOMMENT#" ]; then
    rm_USER_TEXT
  fi
}

#########
# BUILD #
#########

function build_docker() {
  # Check if Docker is installed
  if [ -x "$(command -v docker)" ]; then
    printf "\nDocker installation found.\n"
    # Adding host user requirements to Dockerfile
    sed -i "/#STARTUNCOMMENT#/a $USER_TEXT" Dockerfile
    # Change user in docker-compose.yml to host user
    HOST_USER=$(whoami)
    export HOST_USER
    sed -i "s/\(\/home\/\).*\(\/.Xauthority:\/home\/\).*\(\/.Xauthority\)/\1$HOST_USER\2$HOST_USER\3/g" docker-compose.yml

    ######################################
    # Build MIRACL image from Dockerfile #
    ######################################

    # Printing information about build process and docker-compose.yml to stdout
    printf "\n[+] Building MIRACL and creating docker-compose.yml with the following parameters:\n"
    printf " User: %s\n" "$HOST_USER"
    printf " pid: %s\n" "$(id -u)"
    printf " gid: %s\n" "$(id -g)"
    printf " Max shared memory: %s\n" "$shm_mem"
    printf " Service name: %s\n" "$service_name"
    printf " Image name: %s\n" "$image_name:$miracl_version"
    printf " Container name: %s\n" "$container_name"
    printf " GPU passthrough: %s\n" "${gpu:-false}"
    printf " Script dir mounted: %s\n" "${dev:-true}"
    printf " Log file: %s\n" "${write_log:-false}"
    for v in "${!volumes[@]}"; do
      printf " Volume %s: %s\n" "$v" "${volumes[$v]}"
    done

    # Pass user name, UID and GID to Dockerfile
    function docker_build() {
      docker build \
        --build-arg USER_ID="$(id -u)" \
        --build-arg GROUP_ID="$(id -g)" \
        --build-arg USER="$HOST_USER" \
        -t "$image_name":"$miracl_version" .
    }

    # Check for log flag
    if [ "${write_log}" ]; then
      docker_build | tee build.log
    else
      docker_build
    fi

    # Check if build process exited without errors
    build_status_code=$?
    if [ $build_status_code -eq 0 ]; then
      printf "\nBuild was successful! Checking Docker Compose installation.\n"
      # Remove $USER_TEXT from Dockerfile
      rm_USER_TEXT

      # Test if docker-compose is installed
      # Should come by default with Docker-Desktop
      if [ -x "$(command -v docker-compose)" ]; then
        printf "Docker Compose installation found (%s). Run 'docker-compose up -d' to start the container in the background and then run 'docker exec -it ${container_name} bash' to enter the container.\n" "$(docker-compose --version)"
      elif dcex=$(docker compose version); then
        printf "Docker Compose installation found (%s). Run 'docker compose up -d' or use Docker Desktop (if installed) to start the container in the background and then run 'docker exec -it ${container_name} bash' to enter the container.\n" "$dcex"
      else
        printf "Docker Compose installation not found. Please install Docker Compose plugin or standalone version to run the MIRACL container. Instructions on how to install Docker Compose can be found here: https://docs.docker.com/compose/install/\n"
      fi
    else
      # Return error code if build was not successful
      printf "\nBuild not successful! An error occured with exit code: %s\n" $build_status_code
      # Remove $USER_TEXT from Dockerfile
      rm_USER_TEXT
      # Exit with custom status code
      exit $build_status_code
    fi

  else
    di_status_code=$?
    printf "\nDocker installation not found. Please install Docker first.\n"
    printf "Exiting with status code %s\n" $di_status_code
    # Exit with custom status code
    exit $di_status_code
  fi
}

function main() {
  check_for_sudo
  initialize_variables
  parse_args "$@"
  populate_docker_compose
  populate_dockerfile
  build_docker
}

# Run
main "$@"
