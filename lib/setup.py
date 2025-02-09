from logging import Logger
import os
from typing import Tuple

from lib.sdk.file_repository import FileRepository
from lib.sdk.kernel_plackster_gateway import KernelPlancksterGateway
from lib.sdk.models import ProtocolEnum


def _setup_kernel_planckster(
    logger: Logger,
    kernel_planckster_host: str,
    kernel_planckster_port: int,
    kernel_planckster_auth_token: str,
    kernel_planckster_scheme: str,
) -> KernelPlancksterGateway:

    try:

        logger.info(f"Setting up Kernel Planckster Gateway.")

        # Setup the Kernel Planckster Gateway
        kernel_planckster = KernelPlancksterGateway(
            host=kernel_planckster_host,
            port=kernel_planckster_port,
            auth_token=kernel_planckster_auth_token,
            scheme=kernel_planckster_scheme,
        )
        kernel_planckster.ping()
        logger.info(f"Kernel Planckster Gateway setup successfully.")

        return kernel_planckster

    except Exception as error:
        logger.error(
            f"Unable to setup the Kernel Planckster Gateway. Error:\n{error}"
        )
        raise error


def _setup_file_repository(
    storage_protocol: ProtocolEnum,
    logger: Logger,
) -> FileRepository:

    try:
        logger.info(f"Setting up the File Repository.")

        file_repository = FileRepository(
            protocol=storage_protocol,
        )

        logger.info(f"File Repository setup successfully.")

        return file_repository

    except Exception as error:
        logger.error(f"Unable to setup the File Repository. Error:\n{error}")
        raise error


def setup(
    logger: Logger,
    kp_auth_token: str,
    kp_host: str,
    kp_port: int,
    kp_scheme: str,
) -> Tuple[KernelPlancksterGateway, ProtocolEnum, FileRepository]:
    """
    Setup the Kernel Planckster Gateway, the storage protocol and the file repository.

    NOTE: needs and '.env' file within context.
    """

    try:
        kernel_planckster = _setup_kernel_planckster(
            logger, kp_host, kp_port, kp_auth_token, kp_scheme
        )

        logger.info(f"Checking storage protocol.")
        protocol = ProtocolEnum(os.getenv("STORAGE_PROTOCOL", ProtocolEnum.S3.value))

        if protocol not in [ProtocolEnum.S3, ProtocolEnum.LOCAL]:
            logger.error(f"STORAGE_PROTOCOL must be either 's3' or 'local'.")
            raise ValueError("STORAGE_PROTOCOL must be either 's3' or 'local'.")

        logger.info(f"Storage protocol: {protocol}")

        file_repository = _setup_file_repository(protocol, logger)

        return kernel_planckster, protocol, file_repository

    except Exception as error:
        logger.error(f"Unable to setup. Error:\n{error}")
        raise error
