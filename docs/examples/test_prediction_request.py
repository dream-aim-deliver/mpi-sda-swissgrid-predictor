import os
import requests
import json

def main(port: int, container_name: str):
    try:
        # Define the API endpoint
        URL = f"http://localhost:{port}/predict"

        # Docker cp the ./test_img folder to the /app/ folder
        # This is the folder where the FastAPI container expects the images
        os.system(f"docker cp ./test_img {container_name}:/app/")

        # Hardcoded image paths
        # Make sure you copy these images, from the `img` folder in this repo, to the `/app/test` folder in the FastAPI container
        image_paths = [
            "/app/test_img/2023-01-01_chlorophyll.PNG",
            "/app/test_img/2023-01-01_moisture.PNG",
            "/app/test_img/2023-01-01_natural.PNG",
            "/app/test_img/2023-01-01_optical_thickness.PNG",
            "/app/test_img/2023-01-01_thermal.PNG"
        ]

        # Create JSON payload
        payload = {
            "images": image_paths
        }

        # Send POST request
        response = requests.post(URL, json=payload)

        # Print response
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())
    
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
        "-c",
        "--container_name",
        type=str,
        required=True,
        help="Name of the FastAPI container",
    )

    args = parser.parse_args()

    main(args.port, args.container_name)


if __name__ == "__main__":
    cli()