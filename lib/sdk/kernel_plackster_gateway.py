import logging
import json
import httpx

from lib.sdk.models import KernelPlancksterSourceData



class KernelPlancksterGateway:
    def __init__(self, host: str, port: str, auth_token: str, scheme: str) -> None:
        self._host = host
        self._port = port
        self._client_id = 1  # NOTE: this should match the default client for this project
        self._auth_token = auth_token
        self._scheme = scheme
        self._logger = logging.getLogger(__name__)

    @property
    def url(self) -> str:
        return f"{self._scheme}://{self._host}:{self._port}"

    @property   
    def logger(self) -> logging.Logger:
        return self._logger

    def ping(self) -> bool:
        self.logger.info(f"Pinging Kernel Plankster Gateway at {self.url}")
        res = httpx.get(f"{self.url}/ping")
        self.logger.info(f"Ping response: {res.text}")
        return res.status_code == 200

    def generate_signed_url(self, source_data: KernelPlancksterSourceData) -> str:
        if not self.ping():
            self.logger.error(f"Failed to ping Kernel Plankster Gateway at {self.url}")
            raise Exception("Failed to ping Kernel Plankster Gateway")

        self.logger.info(f"Generating signed url for {source_data.relative_path}")

        endpoint = f"{self.url}/client/{self._client_id}/upload-credentials"

        params = {
            "protocol": source_data.protocol.value,
            "relative_path": source_data.relative_path,
        }

        headers = {
            "Content-Type": "application/json",
            "x-auth-token": self._auth_token,
            }

        res = httpx.get(
            url=endpoint,
            params=params,
            headers=headers,
        )

        self.logger.info(f"Generate signed url response: {res.text}")
        if res.status_code != 200:
            raise ValueError(f"Failed to generate signed url: {res.text}")

        res_json = res.json()

        signed_url = res_json.get("signed_url")

        if not signed_url:
            raise ValueError(f"Failed to generate signed url. Signed URL not found in response. Dumping raw response:\n{res_json}")

        return signed_url
        