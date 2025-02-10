import os
import requests
import pprint

def main(port: int, model_name: str):
    try:
        # Define the API endpoint
        URL = f"http://localhost:{port}/predict"

        # Hardcoded relative paths
        relative_paths = [
            "testCase/testTracer/1/2023-01-01/sentinel/testDataset_thermal_testHash.png",
            "testCase/testTracer/1/2023-01-01/sentinel/testDataset_natural_testHash.png",
            "testCase/testTracer/1/2023-01-01/sentinel/testDataset_optical-thickness_testHash.png",
            "testCase/testTracer/1/2023-01-01/sentinel/testDataset_moisture_testHash.png",
            "testCase/testTracer/1/2023-01-01/sentinel/testDataset_chlorophyll_testHash.png",
        ]

        # Create JSON payload
        payload = {
            "model_name": model_name,
            "relative_paths": relative_paths,
        }

        # Send POST request
        print("Sending POST request to:", URL)
        response = requests.post(URL, json=payload)


        # Print response
        print("\nAPI response:")
        print("Status Code:", response.status_code)
        print("Response JSON:")
        pprint.pprint(response.json())
    
    except Exception as e:
        print("Error:", e)


def cli():
    import argparse

    parser = argparse.ArgumentParser(description="Test the FastAPI container by sending a prediction request")

    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=5000,
        help="Port number of the FastAPI container",
    )

    parser.add_argument(
        "-m",
        "--model_name",
        type=str,
        required=True,
        help="Name of the model to use for prediction",
    )

    args = parser.parse_args()

    main(
        port=args.port,
        model_name=args.model_name
    )


if __name__ == "__main__":
    cli()