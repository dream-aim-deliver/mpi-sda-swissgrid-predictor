import sys

sys.path.append("../..")

from lib.predict_endpoint import IMAGE_SEQUENCE
from lib.sdk.file_repository import FileRepository
from lib.sdk.kernel_plackster_gateway import KernelPlancksterGateway
from lib.sdk.models import KernelPlancksterRelativePath, KernelPlancksterSourceData, ProtocolEnum
from lib.sdk.utils import generate_relative_path


def main():

    try:

        file_repository = FileRepository(
            protocol="s3"
        )

        kernel_planckster_gateway = KernelPlancksterGateway(
            host="localhost",
            port="8000",
            auth_token="test123",
            scheme="http"
        )

        if not kernel_planckster_gateway.ping():
            raise Exception("Failed to ping Kernel Plankster Gateway! Is it running?")

        img_filenames = [f"2023-01-01_{img_type}.png" for img_type in IMAGE_SEQUENCE]

        img_local_paths = [f"test_img/{img_filename}" for img_filename in img_filenames]

        rel_paths = [
            KernelPlancksterRelativePath(
                case_study_name="testCase",
                tracer_id="testTracer",
                job_id="1",
                timestamp="2023-01-01",
                dataset="testDataset",
                evalscript_name=img_type,
                image_hash="testHash",
                file_extension="png"
            )
            for img_type in IMAGE_SEQUENCE
        ]

        source_data = [
            KernelPlancksterSourceData(
                name=f"{rel_path.image_hash}_{rel_path.evalscript_name}",
                protocol=ProtocolEnum.S3,
                relative_path=rel_path.to_str()
            )
            for rel_path in rel_paths
        ]

        print("\n\n\t=> Uploading images to Kernel Planckster...\n")
        for sd, local_path in zip(source_data, img_local_paths):

            print(f"Uploading {local_path} to Kernel Planckster.")
            print(f"Relative path will be: {sd.relative_path}\n")


            signed_url = kernel_planckster_gateway.generate_signed_url_for_upload(
                source_data = sd
            )
            file_repository.public_upload(
                signed_url=signed_url,
                file_path=local_path
            )
            res = kernel_planckster_gateway.register_new_source_data(
                source_data=sd
            )

            print(res)
            print()
        
        print(f"Images uploaded successfully to Kernel Planckster!")
        print(f"Relative paths:\n{"\n".join([sd.relative_path for sd in source_data])}\n")

    except Exception as e:
        print("Error:", e)


def cli():
    main()


if __name__ == "__main__":
    cli()