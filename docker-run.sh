#!/usr/bin/env bash


# Load the environment variables from .env
set -a
source .env
set +a


# Check that all environment variables are set
if [ -z "$MODEL_BASEPATH"] || [ -z "$MODEL_FILENAME" ] || [ -z "$KP_HOST" ] || [ -z "$KP_PORT" ] || [ -z "$KP_SCHEME" ] || [ -z "$KP_AUTH_TOKEN" ]; then
    echo "MODEL_BASEPATH, MODEL_FILENAME, KP_HOST, KP_PORT, KP_SCHEME and KP_AUTH_TOKEN must be set in the .env file. Aborting."
    exit 1
fi

if [ "$MODEL_FILENAME" == "Unified_Beznau_model.keras" ] || [ "$MODEL_FILENAME" == "Unified_model.keras" ]; then

    if [ "$MODEL_FILENAME" == "Unified_Beznau_model.keras" ]; then
        MODEL="Beznau"

    else
        MODEL="Unified"

    fi

else
    echo "The MODEL_FILENAME must be either 'Unified_Beznau_model.keras' or 'Unified_model.keras'. Aborting."
    exit 1
fi


# Run the docker container
docker run --rm \
    --name "mpi-sda-swissgrid-predictor-${MODEL}" \
    -p 5000:5000 \
    -e MODEL_BASEPATH="${MODEL_BASEPATH}" \
    -e MODEL_FILENAME="${MODEL_FILENAME}" \
    -e KP_HOST="${KP_HOST}" \
    -e KP_PORT="${KP_PORT}" \
    -e KP_SCHEME="${KP_SCHEME}" \
    -e KP_AUTH_TOKEN="${KP_AUTH_TOKEN}" \
    mpi-sda-swissgrid-predictor
