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
  local logged_in_user
  logged_in_user=$(logname)

  if [ "$(id -u)" -eq 0 ]; then
    printf "\nError: This script will not work with 'sudo'. Please run it without 'sudo', as the user on your host system (%s) who will be using MIRACL.\n\nInfo: In case you are using 'sudo' because docker requires 'sudo' privileges, create a 'docker' group and add your host user to it. This should allow you to use Docker without 'sudo'.\n\nInfo: For more information on how to create a 'docker' group and add your host user, visit the official Docker docs: https://docs.docker.com/engine/install/linux-postinstall/\n" "${logged_in_user}"
    exit 1
  fi
}

function random_docker_names_generator() {
  random_surnames=("darwin" "einstein" "newton" "tesla" "curie" "turing" "hawking" "feynman" "planck" "galilei" "schroedinger" "heisenberg" "kepler" "lovelace" "hubble" "maxwell" "faraday" "bohr" "pauling" "copernicus" "mendeleev" "roentgen" "koch" "lamarck" "linnaeus" "mendel" "stallman" "torvalds" "moolenaar" "ramanujan" "euler" "knuth" "cavendish" "brahe" "boyle" "murray" "sagan" "watt" "alhazen" "nobel" "gates" "hertz" "berzelius" "fermi" "nash" "snell" "galois" "descartes" "laplace" "riemann" "wheeler" "shannon" "dijkstra" "sherrington" "gibbs" "dunlop" "fleming" "wright" "jefferson" "seaborg" "bardeen" "witten" "hughes" "charles" "bohr" "karl" "pauling" "coulomb" "bragg" "hubble" "schmidt" "kirk" "spock" "mccoy" "sulu" "ura" "scott" "pike" "mudd" "rand" "checkov" "uhura" "data" "riker" "laforge" "picard" "crusher" "guinan" "yar" "worf" "troi" "dax" "sisko" "kira" "bashir" "odo" "quark" "jacob" "bashir" "kassidy" "janeway" "chakotay" "seven" "kim" "neelix" "paris" "tuvok" "balana")

  local logged_in_user
  logged_in_user=$(logname)

  random_surname=${random_surnames[$RANDOM % ${#random_surnames[@]}]}
  random_digits=$((RANDOM % 100000))

  random_container_name="miracl_${logged_in_user}_${random_surname}_${random_digits}"
  random_image_name="${random_container_name}_img"
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
  image_name="${random_image_name}"

  # Set default container name
  container_name="${random_container_name}"

  # Set default image version
  miracl_version="latest"

  # Version file version
  miracl_version_file=$(cat ./miracl/version.txt)

  if [[ ! ${miracl_version_file} =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Invalid version number format. Please check './miracl/version.txt' and make sure the version number is in the correct format (e.g. '2.4.0' or '1.14.2')"
    exit 1
  fi

  # Set container memory size limit
  if [[ "$os" == "Linux" ]]; then
    shm_mem=$(grep MemTotal /proc/meminfo | awk '{printf "%dmb", int($2/1024*0.85)}')
  elif [[ "$os" == "Darwin" ]]; then
    shm_mem=$(sysctl hw.memsize | awk '{printf "%dmb", int($2/1024/1024*0.85)}')
  else
    echo "Unsupported operating system: $os"
    exit 1
  fi

  # Set default for GPU passthrough
  # Setting the flag enables GPU passthrough
  : "${gpu:=false}"

  # Set default for the result from the GPU checks for err msg in final
  # user output msg
  gpu_check_results=true

  # Set default for mounting MIRACL's script folder into container
  # Setting the flag disables mounting
  : "${dev:=false}"

  # Set default to write log file
  # Setting flag writes log file
  : "${write_log:=false}"

  # Set default for interactive prompt data location
  interactive_prompt_data_location=false

  # Set array to capture volumes
  volumes=()

  # Base usage
  base_usage="Usage: ./$(basename "$0") [-n service_name] [-i image_name] [-c container_name] [-t {auto, x.x.x}] [-g] [-e] [-v vol:vol] [-l] [-s] [-m] [-h]"
}

######################
# INTERACTIVE PROMPT #
######################

# Function to prompt for valid input
function prompt_yes_no() {
  local prompt="$1"
  local var_name="$2"
  local default_value="$3"
  local alt_value="$4"

  while true; do
    read -r -p "$prompt ($alt_value/$default_value): " input

    # Set the default value if no input is given
    input="${input:-$default_value}"

    # Normalize input to lowercase for case insensitivity
    case "${input,,}" in
    y | yes)
      eval "${var_name}=true"
      break
      ;;
    n | no)
      eval "${var_name}=false"
      break
      ;;
    *)
      echo "Invalid input. Please enter 'y', 'n', 'Y', 'N', 'Yes', or 'No' or press enter to use the default value."
      ;;
    esac
  done
}

function validate_name_input() {
  local input_var="$1"
  echo "${input_var}" | grep -qP '^[a-zA-Z0-9._/-]+$' || {
    echo "Error: Invalid name '${input_var}'. Only alphanumeric characters, dashes (-), underscores (_), forward slashes (/), and periods (.) are allowed."
    return 1 # Invalid input
  }

  return 0
}

function prompt_image_name() {
  default_image_name="${image_name}"
  while true; do
    read -r -p "Enter Docker image name (default: '${default_image_name}'): " input_image_name
    image_name="${input_image_name:-${default_image_name}}"

    if validate_name_input "${image_name}"; then
      break
    fi
  done
}

function prompt_container_name() {
  default_container_name="${container_name}"
  while true; do
    read -r -p "Enter Docker container name (default: '${default_container_name}'): " input_container_name
    container_name="${input_container_name:-${default_container_name}}"

    if validate_name_input "$container_name"; then
      break
    fi
  done
}

function validate_data_path_input() {
  local input_var="$1"
  if [ -d "${1}" ]; then
    return 0
  else
    echo "The path you enter does not exist on the host system. Please enter a valid path."
    return 1
  fi
}

function prompt_data_folder() {
  interactive_data_location_container="/data"
  while true; do
    read -e -r -p "Enter the location of your data on your host system (default: None). If you choose a location, your data will be mounted at '/data' in your container: " input_data_location_host

    interactive_data_location_host="${input_data_location_host:-false}"

    if [[ ${interactive_data_location_host} != false ]]; then
      interactive_data_location_host="${interactive_data_location_host%/}" # Remove trailing slash
      if [[ "${interactive_data_location_host}" != /* ]]; then             # Prepend slash if not present
        interactive_data_location_host="/${interactive_data_location_host}"
      fi
      if validate_data_path_input "${interactive_data_location_host}"; then
        interactive_prompt_data_location="${interactive_data_location_host}:${interactive_data_location_container}"
        break
      fi
    else
      break
    fi
  done
}

# Interactive prompt function
function interactive_prompt() {
  echo "No flags provided, starting interactive prompt..."

  prompt_image_name
  prompt_container_name
  prompt_yes_no "Enable GPU in Docker container (required for ACE)" gpu "N" "y"
  # prompt_yes_no "Disable script directory mounting" dev "N" "y"  # Currently disabled to not give beginner user too many options
  # prompt_yes_no "Write build log" write_log "N" "y"  # Currently disabled to not give beginner user too many options
  prompt_data_folder

  # Print final variable values for verification
  # echo "Script directory mounting: $dev"  # Currently disabled to not give beginner user too many options
  # echo "Write build log: $write_log"  # Currently disabled to not give beginner user too many options
  # echo "Docker image name: $image_name"
  # echo "Docker container name: $container_name"
  # echo "GPU enabled: $gpu"
  # echo "Data location: $interactive_prompt_data_location"
}

##########
# PARSER #
##########

function usage() {

  cat <<help_menu

 $base_usage

   Automatically build MIRACL Docker image with pseudo host user.

   If no flags are passed, an interactive prompt will be started to guide you through the installation.

 Options:

   -n, name of the Docker service (randomized default: '${container_name}')
   -i, specify image name (randomized default: '${image_name}')
   -c, specify container name (default: '${service_name}')
   -t, set when using specific MIRACL tag/version. Use 'auto' to parse from 'miracl/version.txt' or specify version as floating point value in format 'x.x.x' (default: '${miracl_version}')
   -g, enable Nvidia GPU passthrough mode for Docker container which is required for some of MIRACL's scripts e.g. ACE segmentation (default: ${gpu})
   -e, disable mounting MIRACL's script directory into Docker container. Mounting is useful if you want host changes to propagate to the container directly (default: ${dev}; set flag to disable)
   -d, set shared memory (shm) size (e.g. '1024mb', '16gb' or '512gb') which is important for e.g ACE (default: int(MemTotal/1024)*0.85 of host machine)
   -v, mount volumes for MIRACL in docker-compose.yml, using a separate flag for each additional volume (format: '/path/on/host:/path/in/container'; default: none)
   -l, write logfile of build process to 'build.log' in MIRACL root directory (default: ${write_log})
   -s, print version of build script and exit
   -m, print version of MIRACL on current Git branch and exit
   -h, print this help menu and exit

 Script version: ${version}
 MIRACL version: ${miracl_version_file}

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
      dev=true
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

#!/bin/bash

function check_gpu() {
  # Check if nvidia-smi is available (NVIDIA driver installed)
  if ! command -v nvidia-smi &>/dev/null; then
    echo "ERROR: nvidia-smi command not found. Make sure the NVIDIA driver and CUDA are installed." >&2
    return 1
  fi

  # Check if any GPUs are detected by nvidia-smi
  gpu_count=$(nvidia-smi --query-gpu=count --format=csv,noheader,nounits | wc -l)

  if [[ "$gpu_count" -gt 0 ]]; then
    echo "Found $gpu_count Nvidia GPU(s) on your system."
    return 0
  else
    echo "No Nvidia GPUs found or GPUs are not accessible." >&2
    return 1
  fi
}

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

  if [[ "${gpu}" == true ]]; then

    if ! check_gpu; then
      echo "Warning: GPU support requested but no GPU's found or accessible. Continuing without GPU support."
      gpu_check_results=false
    else
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
  fi

  # Append required volumes
  cat >>docker-compose.yml <<EOF
    volumes:
      - /home/josmann/.Xauthority:/home/josmann/.Xauthority
EOF

  # Append MIRACL scripts folder mounting
  if [[ ${dev} == false ]]; then

    install_script_dir=$(dirname "$(readlink -f "$0")")

    cat >>docker-compose.yml <<EOF
      - ${install_script_dir}/miracl:/code/miracl
EOF
  fi

  # Add additional volumes
  # Check if interactive data location was provided
  if [[ ${interactive_prompt_data_location} != false ]]; then
    volumes+=("${interactive_prompt_data_location}")
  fi

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
    printf " GPU passthrough: %s\n" "${gpu}"
    printf " Script dir mounting disabled: %s\n" "${dev}"
    printf " Log file: %s\n" "${write_log}"
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
      printf "\nBuild was successful!\n"
      # Remove $USER_TEXT from Dockerfile
      rm_USER_TEXT

      if [[ "${gpu_check_results}" == "false" ]]; then
        printf "\n##############################################################"
        printf "\n\nNote: You requested GPU forwarding but no Nvidia GPU's were detected during the initial system check.\n\nIf you think the checks were incorrect, please add the following to your 'docker-compose.yml':\n\n"
        cat <<EOF
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
EOF

        printf "\n\nAdd this under the 'shm_size' entry with 'deploy' being at the same indentation level."
        printf "\n\n##############################################################\n\n"
      fi

      # Test if docker-compose is installed
      # Should come by default with Docker-Desktop
      printf "Checking Docker Compose installation...\n\n"

      if [ -x "$(command -v docker-compose)" ]; then
        printf "Docker Compose installation found (%s).\n\nRun 'docker-compose up -d'\n\nto start the container in the background and then run\n\n'docker exec -it ${container_name} bash'\n\nto enter the container.\n\n" "$(docker-compose --version)"
      elif dcex=$(docker compose version); then
        printf "Docker Compose installation found (%s). Run\n\n'docker compose up -d'\n\nor use Docker Desktop (if installed) to start the container in the background and then run\n\n'docker exec -it ${container_name} bash'\n\nto enter the container.\n\n" "$dcex"
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

##############
# MAIN LOGIC #
##############

# Run interactive prompt if no flags are provided
function main() {
  check_for_sudo
  random_docker_names_generator
  initialize_variables
  if [ $# -eq 0 ]; then
    interactive_prompt
  fi
  parse_args "$@"
  populate_docker_compose
  populate_dockerfile
  build_docker
}

# Run
main "$@"
