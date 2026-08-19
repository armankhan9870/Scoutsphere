"""Abstract StorageClient interface and LocalStorageClient implementation for resume files."""

import os
import uuid
from abc import ABC, abstractmethod
from typing import Tuple

import aiofiles

from app.core.logging import logger

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../uploads/resumes"))


class StorageClient(ABC):
    """Abstract file storage client interface."""

    @abstractmethod
    async def save_file(self, file_bytes: bytes, original_filename: str) -> Tuple[str, str]:
        """Saves file bytes and returns a tuple of (stored_relative_path, unique_file_id)."""
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Deletes a file given its path."""
        pass


class LocalStorageClient(StorageClient):
    """Local disk storage client implementation for development environments."""

    def __init__(self, base_dir: str = UPLOAD_DIR):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    async def save_file(self, file_bytes: bytes, original_filename: str) -> Tuple[str, str]:
        """Saves file bytes to local disk with a unique UUID filename."""
        ext = os.path.splitext(original_filename)[1].lower() or ".pdf"
        file_id = str(uuid.uuid4())
        unique_filename = f"{file_id}{ext}"
        destination_path = os.path.join(self.base_dir, unique_filename)

        async with aiofiles.open(destination_path, "wb") as f:
            await f.write(file_bytes)

        logger.info("Saved upload file to local disk: %s", destination_path)
        return destination_path, file_id

    async def delete_file(self, file_path: str) -> bool:
        """Removes a file from local disk."""
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info("Deleted file from local disk: %s", file_path)
            return True
        return False


def get_storage_client() -> StorageClient:
    """Factory dependency returning configured storage client."""
    return LocalStorageClient()
