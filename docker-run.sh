#!/usr/bin/env bash

# Load the environment variables from .env
echo "=> Loading environment variables from .env file..."
set -a
source .env
set +a

# Check that all environment variables are set
if [ -z "$KP_HOST" ] || [ -z "$KP_PORT" ] || [ -z "$KP_SCHEME" ] || [ -z "$KP_AUTH_TOKEN" ]; then
    echo "MODEL_BASEPATH, MODEL_FILENAME, KP_HOST, KP_PORT, KP_SCHEME and KP_AUTH_TOKEN must be set in the .env file. Aborting."
    exit 1
fi

echo "=> Successfully loaded environment variables from .env file."


# Run the docker container
echo "=> Running the docker container..."
CONTAINER_NAME="mpi-sda-swissgrid-predictor"
printf "=> Container name: ${CONTAINER_NAME}\n"

docker run --rm \
    --name "${CONTAINER_NAME}" \
    -p 5000:5000 \
    -e KP_HOST="${KP_HOST}" \
    -e KP_PORT="${KP_PORT}" \
    -e KP_SCHEME="${KP_SCHEME}" \
    -e KP_AUTH_TOKEN="${KP_AUTH_TOKEN}" \
    mpi-sda-swissgrid-predictor
