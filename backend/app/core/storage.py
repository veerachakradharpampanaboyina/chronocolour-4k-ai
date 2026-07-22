"""
ChronoColor 4K AI — Storage Client

Provides S3-compatible object storage for videos, frames, and results.
Supports local filesystem fallback for development without Docker/MinIO.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO

import structlog
from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from app.config import Settings

logger = structlog.get_logger(__name__)

# Module-level client reference
_s3_client = None
_local_storage: LocalStorage | None = None
_settings: Settings | None = None
_use_local: bool = False


class LocalStorage:
    """Local filesystem storage that mimics the S3 interface."""

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info("local_storage_initialized", base_dir=str(self.base_dir))

    def _bucket_path(self, bucket: str) -> Path:
        p = self.base_dir / bucket
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _file_path(self, bucket: str, key: str) -> Path:
        fp = self._bucket_path(bucket) / key
        fp.parent.mkdir(parents=True, exist_ok=True)
        return fp

    def create_bucket(self, bucket: str) -> None:
        self._bucket_path(bucket)
        logger.info("local_bucket_created", bucket=bucket)

    def head_bucket(self, bucket: str) -> bool:
        return self._bucket_path(bucket).exists()

    def upload_fileobj(self, file_obj: BinaryIO, bucket: str, key: str, content_type: str = "") -> str:
        fp = self._file_path(bucket, key)
        with open(fp, "wb") as f:
            shutil.copyfileobj(file_obj, f)
        logger.info("local_file_uploaded", bucket=bucket, key=key, size=fp.stat().st_size)
        return key

    def upload_file(self, file_path: str, bucket: str, key: str, content_type: str = "") -> str:
        dest = self._file_path(bucket, key)
        shutil.copy2(file_path, dest)
        logger.info("local_file_uploaded", bucket=bucket, key=key, source=file_path)
        return key

    def download_file(self, bucket: str, key: str, file_path: str) -> str:
        src = self._file_path(bucket, key)
        if not src.exists():
            raise FileNotFoundError(f"File not found: {bucket}/{key}")
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, file_path)
        logger.info("local_file_downloaded", bucket=bucket, key=key, dest=file_path)
        return file_path

    def generate_presigned_url(self, bucket: str, key: str, expires_in: int = 3600) -> str:
        fp = self._file_path(bucket, key)
        if _settings and getattr(_settings, "next_public_api_url", None):
            base_url = _settings.next_public_api_url.rstrip("/")
            return f"{base_url}/api/v1/storage/{bucket}/{key}"
        return f"/api/v1/storage/{bucket}/{key}"

    def delete_object(self, bucket: str, key: str) -> None:
        fp = self._file_path(bucket, key)
        if fp.exists():
            fp.unlink()
            logger.info("local_file_deleted", bucket=bucket, key=key)

    def list_objects_v2(self, bucket: str, prefix: str = "") -> dict:
        bp = self._bucket_path(bucket)
        prefix_path = bp / prefix if prefix else bp
        files = []
        if prefix_path.exists():
            for fp in prefix_path.rglob("*"):
                if fp.is_file():
                    rel = fp.relative_to(bp)
                    stat = fp.stat()
                    files.append({
                        "Key": str(rel).replace("\\", "/"),
                        "Size": stat.st_size,
                        "LastModified": __import__("datetime").datetime.fromtimestamp(
                            stat.st_mtime, tz=__import__("datetime").timezone.utc
                        ),
                    })
        return {"Contents": files}


async def init_storage(settings: Settings) -> None:
    """
    Initialize storage client and create required buckets.

    Args:
        settings: Application settings with storage credentials.
    """
    global _s3_client, _local_storage, _settings, _use_local
    _settings = settings
    _use_local = settings.use_local_services

    if _use_local:
        # Use local filesystem storage on configured directory (e.g. D:\chronocolor_storage)
        base_dir = getattr(settings, "local_storage_dir", "D:\\chronocolor_storage")
        try:
            os.makedirs(base_dir, exist_ok=True)
        except Exception as e:
            logger.warning("local_storage_dir_creation_failed", path=base_dir, error=str(e))
            base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "..", "local_storage")
            os.makedirs(base_dir, exist_ok=True)

        _local_storage = LocalStorage(os.path.abspath(base_dir))

        for bucket_name in settings.all_storage_buckets:
            _local_storage.create_bucket(bucket_name)

        logger.info("storage_connected_local", base_dir=str(_local_storage.base_dir), buckets=settings.all_storage_buckets)
    else:
        import boto3
        from botocore.config import Config as BotoConfig

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
        try:
            for bucket_name in settings.all_storage_buckets:
                try:
                    _s3_client.head_bucket(Bucket=bucket_name)
                    logger.info("bucket_exists", bucket=bucket_name)
                except ClientError:
                    _s3_client.create_bucket(Bucket=bucket_name)
                    logger.info("bucket_created", bucket=bucket_name)
            logger.info("storage_connected", buckets=settings.all_storage_buckets)
        except Exception as e:
            logger.warning("storage_connection_warning", error=str(e))


def get_s3_client():
    """Get the S3 client instance (or local storage wrapper)."""
    if _use_local:
        if _local_storage is None:
            raise RuntimeError("Storage not initialized. Call init_storage() first.")
        return _local_storage
    if _s3_client is None:
        raise RuntimeError("Storage not initialized. Call init_storage() first.")
    return _s3_client


def get_storage_settings() -> "Settings":
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
    Upload a file to S3/MinIO or local storage.

    Args:
        file_obj: File-like object to upload.
        bucket: Target bucket name.
        key: Object key (path within bucket).
        content_type: MIME type of the file.

    Returns:
        The S3 object key.
    """
    client = get_s3_client()
    if _use_local:
        client.upload_fileobj(file_obj, bucket, key, content_type)
    else:
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
    Upload a file from disk to S3/MinIO or local storage.

    Args:
        file_path: Local file path to upload.
        bucket: Target bucket name.
        key: Object key (path within bucket).
        content_type: MIME type of the file.

    Returns:
        The S3 object key.
    """
    client = get_s3_client()
    if _use_local:
        client.upload_file(file_path, bucket, key, content_type)
    else:
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
    Download a file from S3/MinIO or local storage to local disk.

    Args:
        bucket: Source bucket name.
        key: Object key.
        file_path: Local destination path.

    Returns:
        The local file path.
    """
    client = get_s3_client()
    if _use_local:
        client.download_file(bucket, key, file_path)
    else:
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
    if _use_local:
        return client.generate_presigned_url(bucket, key, expires_in)
    url = client.generate_presigned_url(
        method,
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
    )
    return url


def delete_file(bucket: str, key: str) -> None:
    """Delete a file from S3/MinIO or local storage."""
    client = get_s3_client()
    if _use_local:
        client.delete_object(bucket, key)
    else:
        client.delete_object(Bucket=bucket, Key=key)
    logger.info("file_deleted", bucket=bucket, key=key)


def list_files(bucket: str, prefix: str = "") -> list[dict]:
    """
    List files in a bucket with optional prefix filter.

    Returns:
        List of dicts with 'key', 'size', 'last_modified'.
    """
    client = get_s3_client()
    if _use_local:
        response = client.list_objects_v2(bucket, prefix)
    else:
        response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)

    files = []
    for obj in response.get("Contents", []):
        files.append({
            "key": obj["Key"],
            "size": obj["Size"],
            "last_modified": obj["LastModified"].isoformat(),
        })

    return files
