from enum import Enum
from pydantic import BaseModel


class BaseJobState(Enum):
    CREATED = "created"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"

class ProtocolEnum(Enum):
    """
    The storage protocol to use for a file.

    Attributes:
    - S3: S3
    - LOCAL: Local  @deprecated
    """
    S3 = "s3"
    LOCAL = "local"

class KernelPlancksterRelativePath(BaseModel):
    case_study_name: str
    tracer_id: str
    job_id: str
    timestamp: str
    dataset: str
    evalscript_name: str
    image_hash: str
    file_extension: str

    def to_str(self) -> str:
        return f"{self.case_study_name}/{self.tracer_id}/{self.job_id}/{self.timestamp}/sentinel/{self.dataset}_{self.evalscript_name}_{self.image_hash}.{self.file_extension}"


class KernelPlancksterSourceData(BaseModel):
    """
    Synchronize this with Kernel Planckster's SourceData model, so that this client generates valid requests.

    @attr name: the name of the source data to register as metadata
    @attr protocol: the protocol to use to store the source data
    @attr relative_path: the relative path to store the source data in the storage system
    """
    name: str
    protocol: ProtocolEnum
    relative_path: str

    def to_json(cls) -> str:
        """
        Dumps the model to a json formatted string. Wrapper around pydantic's model_dump_json method: in case they decide to deprecate it, we only refactor here.
        """
        return cls.model_dump_json()

    def __str__(self) -> str:
        return self.to_json()

    @classmethod
    def from_json(cls, json_str: str) -> "KernelPlancksterSourceData":
        """
        Loads the model from a json formatted string. Wrapper around pydantic's model_validate_json method: in case they decide to deprecate it, we only refactor here.
        """
        return cls.model_validate_json(json_data=json_str)
