FROM labg/mpi-sda-swissgrid-predictor-conda-environment

WORKDIR /app

# Install additional dependencies without touching the base image
RUN conda run -n sentinel pip install httpx pydantic

COPY app.py /app/
COPY lib /app/lib

EXPOSE 5000

# Command to run the Flask application
CMD ["conda", "run", "-n", "sentinel", "python", "app.py"]
