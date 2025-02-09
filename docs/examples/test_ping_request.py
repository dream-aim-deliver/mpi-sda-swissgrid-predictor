import requests


def main(port: int):

    URL = f"http://localhost:{port}/"

    try:
        response = requests.get(URL)

        print("Status Code:", response.status_code)
        print("Response Text:", response.text)

    except Exception as e:
        print(f"\t→ Error sending request:\n{str(e)}")


def cli():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=5000,
        help="Port number of the FastAPI server",
    )

    args = parser.parse_args()

    main(port=args.port)


if __name__ == "__main__":
    cli()