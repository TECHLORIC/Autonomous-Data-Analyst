import tempfile
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from pathlib import Path
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.use_s3 = bool(settings.s3_bucket_name)
        if self.use_s3:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                endpoint_url=settings.s3_endpoint_url
            )
            self.bucket = settings.s3_bucket_name
        else:
            self.local_storage_dir = Path("storage/uploads")
            self.local_storage_dir.mkdir(parents=True, exist_ok=True)

    async def upload_file(self, file_bytes: bytes, filename: str) -> str:
        """Uploads a file and returns the storage path/key."""
        if self.use_s3:
            try:
                # Synchronous boto3 call in async context, in a real production env
                # this would use aioboto3 or be run in a thread pool.
                # For this implementation, we run it as is.
                self.s3_client.put_object(
                    Bucket=self.bucket,
                    Key=filename,
                    Body=file_bytes
                )
                return f"s3://{self.bucket}/{filename}"
            except (NoCredentialsError, ClientError) as e:
                logger.error(f"S3 upload failed: {str(e)}")
                raise
        else:
            file_path = self.local_storage_dir / filename
            file_path.write_bytes(file_bytes)
            return str(file_path)

    def download_to_temp_file(self, storage_path: str) -> str:
        """Downloads from storage to a local temporary file and returns the temp path."""
        if self.use_s3 and storage_path.startswith("s3://"):
            key = storage_path.replace(f"s3://{self.bucket}/", "")
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(key).suffix)
            self.s3_client.download_file(self.bucket, key, temp_file.name)
            return temp_file.name
        else:
            # If not S3, it's already a local file path
            return storage_path

storage = StorageService()
