FROM labg/mpi-sda-swissgrid-predictor-conda-environment

WORKDIR /app

COPY app.py /app/

EXPOSE 5000

# Command to run the Flask application
CMD ["conda", "run", "-n", "sentinel", "python", "app.py"]
