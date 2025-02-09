

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


### Running the Docker Container

```sh
docker run --name mpi-sda-swissgrid-predictor -p 5000:5000 mpi-sda-swissgrid-predictor
```


### Development & Testing

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install .[dev]
```

Then you can run the scripts in the `docs/examples` folder.

```sh
python docs/examples/test_ping_request.py
```

For a more substantial test of the prediction, start the container, and then copy the test files into the container:

```sh
docker cp docs/examples/test_img test:/app
```

Then you can run the test script:

```sh
python docs/examples/test_prediction_request.py
```
