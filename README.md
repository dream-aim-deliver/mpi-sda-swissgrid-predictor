# MPI-SDA Swissgrid Predictor

### Building the Docker Container


```sh
docker build -t mpi-sda-swissgrid-predictor . --load
```

If you experience any problems while building, or if the build is not including any new files or changes, you can try to build the container with the `--no-cache` option and the `--pull` option to ensure that the base image is up-to-date:

```sh
docker build --pull --no-cache -t mpi-sda-swissgrid-predictor . --load
```

The `baseDockerfile` includes the build for the base image used in the main `Dockerfile`, but it's not necessary to build the former as `Dockerfile` pulls a pre-built image from Docker Hub.
It is split like so because the setup of the conda environment is time-consuming and does not need to be repeated for every build.


### Running the Docker Container Locally

A utility file called `docker-run.sh` is provided to run the container with the correct options.
You need to configure a `.env`, by following the `.env.example` file, to set the environment variables for the container.

Then you can simply run the script:

```sh
./docker-run.sh
```

If everything worked correctly, you should see the container name printed to the console.


### Development & Testing

To test the container locally, you can run the container and then run the test scripts from the `docs/examples` folder.
To do so, you need to install the development dependencies in a virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r dev-requirements.txt
```

Then you can run the scripts in the `docs/examples` folder.

For a simple check that the container is running and the API is reachable:

```sh
python docs/examples/test_ping_request.py
```

For a more substantial test of the prediction:
- Build the container using the `Dockerfile`, with the correct `.env` file matching your Kernel Planckster instance
- Run the container using the `docker-run.sh` script
- Then:

```sh
cd docs/examples
python upload_images_to_kp.py  # Will upload test images to Kernel Planckster
python test_prediction_request.py -n "model-name"
```

Where `model-name` is one of the supported models. E.g., "Beznau", "Unified".
