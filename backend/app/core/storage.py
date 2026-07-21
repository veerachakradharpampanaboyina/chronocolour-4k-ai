"""
ChronoColor 4K AI — MinIO / S3 Storage Client

Provides S3-compatible object storage for videos, frames, and results.
Handles bucket initialization, upload, download, and presigned URLs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, BinaryIO

import boto3
import structlog
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from app.config import Settings

logger = structlog.get_logger(__name__)

# Module-level client reference
_s3_client = None
_settings: Settings | None = None


async def init_storage(settings: Settings) -> None:
    """
    Initialize MinIO/S3 client and create required buckets.

    Args:
        settings: Application settings with storage credentials.
    """
    global _s3_client, _settings
    _settings = settings

    logger.info("connecting_to_storage", endpoint=settings.storage_endpoint)

    _s3_client = boto3.client(
        "s3",
        endpoint_url=settings.storage_url,
        aws_access_key_id=settings.storage_access_key,
        aws_secret_access_key=settings.storage_secret_key,
        region_name=settings.storage_region,
        config=BotoConfig(
            signature_version="s3v4",
            retries={"max_attempts": 3, "mode": "adaptive"},
        ),
    )

    # Create buckets if they don't exist
    for bucket_name in settings.all_storage_buckets:
        try:
            _s3_client.head_bucket(Bucket=bucket_name)
            logger.info("bucket_exists", bucket=bucket_name)
        except ClientError:
            _s3_client.create_bucket(Bucket=bucket_name)
            logger.info("bucket_created", bucket=bucket_name)

    logger.info("storage_connected", buckets=settings.all_storage_buckets)


def get_s3_client():
    """Get the S3 client instance."""
    if _s3_client is None:
        raise RuntimeError("Storage not initialized. Call init_storage() first.")
    return _s3_client


def get_storage_settings() -> Settings:
    """Get storage-related settings."""
    if _settings is None:
        raise RuntimeError("Storage not initialized. Call init_storage() first.")
    return _settings


def upload_file(
    file_obj: BinaryIO,
    bucket: str,
    key: str,
    content_type: str = "application/octet-stream",
) -> str:
    """
    Upload a file to S3/MinIO.

    Args:
        file_obj: File-like object to upload.
        bucket: Target bucket name.
        key: Object key (path within bucket).
        content_type: MIME type of the file.

    Returns:
        The S3 object key.
    """
    client = get_s3_client()
    client.upload_fileobj(
        file_obj,
        bucket,
        key,
        ExtraArgs={"ContentType": content_type},
    )
    logger.info("file_uploaded", bucket=bucket, key=key)
    return key


def upload_file_path(
    file_path: str,
    bucket: str,
    key: str,
    content_type: str = "application/octet-stream",
) -> str:
    """
    Upload a file from disk to S3/MinIO.

    Args:
        file_path: Local file path to upload.
        bucket: Target bucket name.
        key: Object key (path within bucket).
        content_type: MIME type of the file.

    Returns:
        The S3 object key.
    """
    client = get_s3_client()
    client.upload_file(
        file_path,
        bucket,
        key,
        ExtraArgs={"ContentType": content_type},
    )
    logger.info("file_uploaded", bucket=bucket, key=key, source=file_path)
    return key


def download_file(bucket: str, key: str, file_path: str) -> str:
    """
    Download a file from S3/MinIO to local disk.

    Args:
        bucket: Source bucket name.
        key: Object key.
        file_path: Local destination path.

    Returns:
        The local file path.
    """
    client = get_s3_client()
    client.download_file(bucket, key, file_path)
    logger.info("file_downloaded", bucket=bucket, key=key, dest=file_path)
    return file_path


def generate_presigned_url(
    bucket: str,
    key: str,
    expires_in: int = 3600,
    method: str = "get_object",
) -> str:
    """
    Generate a presigned URL for direct browser upload/download.

    Args:
        bucket: Bucket name.
        key: Object key.
        expires_in: URL expiry in seconds (default: 1 hour).
        method: S3 method ('get_object' for download, 'put_object' for upload).

    Returns:
        The presigned URL string.
    """
    client = get_s3_client()
    url = client.generate_presigned_url(
        method,
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
    )
    return url


def delete_file(bucket: str, key: str) -> None:
    """Delete a file from S3/MinIO."""
    client = get_s3_client()
    client.delete_object(Bucket=bucket, Key=key)
    logger.info("file_deleted", bucket=bucket, key=key)


def list_files(bucket: str, prefix: str = "") -> list[dict]:
    """
    List files in a bucket with optional prefix filter.

    Returns:
        List of dicts with 'key', 'size', 'last_modified'.
    """
    client = get_s3_client()
    response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)

    files = []
    for obj in response.get("Contents", []):
        files.append({
            "key": obj["Key"],
            "size": obj["Size"],
            "last_modified": obj["LastModified"].isoformat(),
        })

    return files
