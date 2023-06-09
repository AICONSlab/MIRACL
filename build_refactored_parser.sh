#!/bin/bash

# Default values
image="my_image"
name="8080"
container="my_container"
gpu=false
volume="/path/to/volume"
volumes=()

# Parse command line arguments
while getopts ":n:i:c:v:gm:" opt; do
  case ${opt} in
    n )
      image=$OPTARG
      ;;
    i )
      name=$OPTARG
      ;;
    c )
      container=$OPTARG
      ;;
    v )
      volume=$OPTARG
      ;;
    g )
      gpu=true
      ;;
    m )
      volumes+=("$OPTARG")
      ;;
    \? )
      echo "Invalid option: -$OPTARG" 1>&2
      exit 1
      ;;
    : )
      echo "Option -$OPTARG requires an argument." 1>&2
      exit 1
      ;;
  esac
done

# Generate docker-compose.yml file
cat > docker-compose.yml <<EOF
version: "3.3"
services:
  $name:
    image: $image
    tty: true
    environment:
      - DISPLAY
    stdin_open: true
    network_mode: host
    container_name: $container
    volumes:
      - /home/josmann/.Xauthority:/home/josmann/.Xauthority
EOF

# Add additional volumes
for v in "${volumes[@]}"; do
  echo "      - $v" >> docker-compose.yml
done

if [[ $gpu ]]; then

cat >> docker-compose.yml <<EOF
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
EOF

else
  
  printf "No GPU selected\n"

fi

