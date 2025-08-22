"""
MCP Filesystem Server Implementation

This server provides file system operations and management capabilities for the unified content creator system.
It supports file operations, directory management, and file metadata handling.
"""

import hashlib
import json
import logging
import mimetypes
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_BASE_PATH = "data/files"
DEFAULT_MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
DEFAULT_ALLOWED_EXTENSIONS = [
    ".txt",
    ".md",
    ".html",
    ".css",
    ".js",
    ".json",
    ".xml",
    ".csv",
    ".doc",
    ".docx",
    ".pdf",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".ico",
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".wav",
]


@dataclass
class FileInfo:
    """Represents file information and metadata."""

    path: str
    name: str
    size_bytes: int
    file_type: str
    mime_type: str
    created_at: datetime
    modified_at: datetime
    accessed_at: datetime
    permissions: str
    is_directory: bool
    is_file: bool
    is_symlink: bool
    hash_md5: str = ""
    hash_sha256: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass
class DirectoryInfo:
    """Represents directory information."""

    path: str
    name: str
    total_files: int
    total_directories: int
    total_size_bytes: int
    created_at: datetime
    modified_at: datetime
    permissions: str
    contents: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FileOperation:
    """Represents a file operation request."""

    operation: str  # read, write, copy, move, delete, create_dir
    source_path: str
    target_path: str | None = None
    content: str | None = None
    overwrite: bool = False
    create_parents: bool = True
    client_id: str | None = None


@dataclass
class FileOperationResult:
    """Result of a file operation."""

    success: bool
    operation: str
    source_path: str
    target_path: str | None = None
    message: str
    file_info: FileInfo | None = None
    error: str | None = None
    client_id: str | None = None


class FileSystemManager:
    """Manages file system operations with safety checks and metadata tracking."""

    def __init__(self, base_path: str = DEFAULT_BASE_PATH) -> None:
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.allowed_extensions = set(DEFAULT_ALLOWED_EXTENSIONS)
        self.max_file_size = DEFAULT_MAX_FILE_SIZE

        # Create metadata directory
        self.metadata_dir = self.base_path / ".metadata"
        self.metadata_dir.mkdir(exist_ok=True)

    def _is_safe_path(self, path: str) -> bool:
        """Check if a path is safe to operate on (within base directory)."""
        try:
            resolved_path = Path(path).resolve()
            return str(resolved_path).startswith(str(self.base_path))
        except Exception:
            return False

    def _get_file_hash(self, file_path: Path, algorithm: str = "md5") -> str:
        """Calculate file hash using specified algorithm."""
        try:
            if algorithm == "md5":
                hash_obj = hashlib.md5()
            elif algorithm == "sha256":
                hash_obj = hashlib.sha256()
            else:
                return ""

            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)

            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate {algorithm} hash for {file_path}: {e}")
            return ""

    def _get_file_info(self, file_path: Path) -> FileInfo:
        """Get comprehensive file information."""
        try:
            stat = file_path.stat()

            # Get MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                mime_type = "application/octet-stream"

            # Get file type from extension
            file_type = file_path.suffix.lower() if file_path.suffix else "unknown"

            # Calculate hashes for files
            hash_md5 = ""
            hash_sha256 = ""
            if file_path.is_file():
                hash_md5 = self._get_file_hash(file_path, "md5")
                hash_sha256 = self._get_file_hash(file_path, "sha256")

            return FileInfo(
                path=str(file_path),
                name=file_path.name,
                size_bytes=stat.st_size,
                file_type=file_type,
                mime_type=mime_type,
                created_at=datetime.fromtimestamp(stat.st_ctime),
                modified_at=datetime.fromtimestamp(stat.st_mtime),
                accessed_at=datetime.fromtimestamp(stat.st_atime),
                permissions=oct(stat.st_mode)[-3:],
                is_directory=file_path.is_dir(),
                is_file=file_path.is_file(),
                is_symlink=file_path.is_symlink(),
                hash_md5=hash_md5,
                hash_sha256=hash_sha256,
            )
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            raise

    async def read_file(self, file_path: str) -> FileOperationResult:
        """Read file content."""
        try:
            if not self._is_safe_path(file_path):
                return FileOperationResult(
                    success=False,
                    operation="read",
                    source_path=file_path,
                    message="Path is not safe to access",
                    error="Path outside allowed directory",
                )

            path = Path(file_path)
            if not path.exists():
                return FileOperationResult(
                    success=False,
                    operation="read",
                    source_path=file_path,
                    message="File does not exist",
                    error="File not found",
                )

            if not path.is_file():
                return FileOperationResult(
                    success=False,
                    operation="read",
                    source_path=file_path,
                    message="Path is not a file",
                    error="Not a file",
                )

            # Check file size
            if path.stat().st_size > self.max_file_size:
                return FileOperationResult(
                    success=False,
                    operation="read",
                    source_path=file_path,
                    message="File too large to read",
                    error="File size exceeds limit",
                )

            # Read file content
            async with aiofiles.open(path, encoding="utf-8") as f:
                content = await f.read()

            file_info = self._get_file_info(path)

            return FileOperationResult(
                success=True,
                operation="read",
                source_path=file_path,
                message="File read successfully",
                file_info=file_info,
            )

        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return FileOperationResult(
                success=False, operation="read", source_path=file_path, message="Failed to read file", error=str(e)
            )

    async def write_file(
        self, file_path: str, content: str, overwrite: bool = False, create_parents: bool = True
    ) -> FileOperationResult:
        """Write content to file."""
        try:
            if not self._is_safe_path(file_path):
                return FileOperationResult(
                    success=False,
                    operation="write",
                    source_path=file_path,
                    message="Path is not safe to access",
                    error="Path outside allowed directory",
                )

            path = Path(file_path)

            # Check if file exists and overwrite is not allowed
            if path.exists() and not overwrite:
                return FileOperationResult(
                    success=False,
                    operation="write",
                    source_path=file_path,
                    message="File already exists and overwrite not allowed",
                    error="File exists",
                )

            # Create parent directories if requested
            if create_parents:
                path.parent.mkdir(parents=True, exist_ok=True)

            # Check file extension
            if path.suffix.lower() not in self.allowed_extensions:
                return FileOperationResult(
                    success=False,
                    operation="write",
                    source_path=file_path,
                    message="File extension not allowed",
                    error="Extension not permitted",
                )

            # Write file content
            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(content)

            file_info = self._get_file_info(path)

            return FileOperationResult(
                success=True,
                operation="write",
                source_path=file_path,
                message="File written successfully",
                file_info=file_info,
            )

        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            return FileOperationResult(
                success=False, operation="write", source_path=file_path, message="Failed to write file", error=str(e)
            )

    async def create_directory(self, dir_path: str, create_parents: bool = True) -> FileOperationResult:
        """Create a directory."""
        try:
            if not self._is_safe_path(dir_path):
                return FileOperationResult(
                    success=False,
                    operation="create_dir",
                    source_path=dir_path,
                    message="Path is not safe to access",
                    error="Path outside allowed directory",
                )

            path = Path(dir_path)

            if path.exists():
                return FileOperationResult(
                    success=False,
                    operation="create_dir",
                    source_path=dir_path,
                    message="Directory already exists",
                    error="Directory exists",
                )

            # Create directory
            if create_parents:
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.mkdir()

            file_info = self._get_file_info(path)

            return FileOperationResult(
                success=True,
                operation="create_dir",
                source_path=dir_path,
                message="Directory created successfully",
                file_info=file_info,
            )

        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {e}")
            return FileOperationResult(
                success=False,
                operation="create_dir",
                source_path=dir_path,
                message="Failed to create directory",
                error=str(e),
            )

    async def copy_file(self, source_path: str, target_path: str, overwrite: bool = False) -> FileOperationResult:
        """Copy a file from source to target."""
        try:
            if not self._is_safe_path(source_path) or not self._is_safe_path(target_path):
                return FileOperationResult(
                    success=False,
                    operation="copy",
                    source_path=source_path,
                    target_path=target_path,
                    message="Path is not safe to access",
                    error="Path outside allowed directory",
                )

            source = Path(source_path)
            target = Path(target_path)

            if not source.exists():
                return FileOperationResult(
                    success=False,
                    operation="copy",
                    source_path=source_path,
                    target_path=target_path,
                    message="Source file does not exist",
                    error="Source not found",
                )

            if not source.is_file():
                return FileOperationResult(
                    success=False,
                    operation="copy",
                    source_path=source_path,
                    target_path=target_path,
                    message="Source is not a file",
                    error="Source not a file",
                )

            if target.exists() and not overwrite:
                return FileOperationResult(
                    success=False,
                    operation="copy",
                    source_path=source_path,
                    target_path=target_path,
                    message="Target file exists and overwrite not allowed",
                    error="Target exists",
                )

            # Create target directory if needed
            target.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(source, target)

            file_info = self._get_file_info(target)

            return FileOperationResult(
                success=True,
                operation="copy",
                source_path=source_path,
                target_path=target_path,
                message="File copied successfully",
                file_info=file_info,
            )

        except Exception as e:
            logger.error(f"Failed to copy file from {source_path} to {target_path}: {e}")
            return FileOperationResult(
                success=False,
                operation="copy",
                source_path=source_path,
                target_path=target_path,
                message="Failed to copy file",
                error=str(e),
            )

    async def move_file(self, source_path: str, target_path: str, overwrite: bool = False) -> FileOperationResult:
        """Move a file from source to target."""
        try:
            if not self._is_safe_path(source_path) or not self._is_safe_path(target_path):
                return FileOperationResult(
                    success=False,
                    operation="move",
                    source_path=source_path,
                    target_path=target_path,
                    message="Path is not safe to access",
                    error="Path outside allowed directory",
                )

            source = Path(source_path)
            target = Path(target_path)

            if not source.exists():
                return FileOperationResult(
                    success=False,
                    operation="move",
                    source_path=source_path,
                    target_path=target_path,
                    message="Source file does not exist",
                    error="Source not found",
                )

            if target.exists() and not overwrite:
                return FileOperationResult(
                    success=False,
                    operation="move",
                    source_path=source_path,
                    target_path=target_path,
                    message="Target file exists and overwrite not allowed",
                    error="Target exists",
                )

            # Create target directory if needed
            target.parent.mkdir(parents=True, exist_ok=True)

            # Move file
            shutil.move(source, target)

            file_info = self._get_file_info(target)

            return FileOperationResult(
                success=True,
                operation="move",
                source_path=source_path,
                target_path=target_path,
                message="File moved successfully",
                file_info=file_info,
            )

        except Exception as e:
            logger.error(f"Failed to move file from {source_path} to {target_path}: {e}")
            return FileOperationResult(
                success=False,
                operation="move",
                source_path=source_path,
                target_path=target_path,
                message="Failed to move file",
                error=str(e),
            )

    async def delete_file(self, file_path: str) -> FileOperationResult:
        """Delete a file or directory."""
        try:
            if not self._is_safe_path(file_path):
                return FileOperationResult(
                    success=False,
                    operation="delete",
                    source_path=file_path,
                    message="Path is not safe to access",
                    error="Path outside allowed directory",
                )

            path = Path(file_path)

            if not path.exists():
                return FileOperationResult(
                    success=False,
                    operation="delete",
                    source_path=file_path,
                    message="File does not exist",
                    error="File not found",
                )

            # Delete file or directory
            if path.is_file():
                path.unlink()
            else:
                shutil.rmtree(path)

            return FileOperationResult(
                success=True, operation="delete", source_path=file_path, message="File deleted successfully"
            )

        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return FileOperationResult(
                success=False, operation="delete", source_path=file_path, message="Failed to delete file", error=str(e)
            )

    async def list_directory(self, dir_path: str) -> list[FileInfo]:
        """List contents of a directory."""
        try:
            if not self._is_safe_path(dir_path):
                return []

            path = Path(dir_path)
            if not path.exists() or not path.is_dir():
                return []

            files = []
            for item in path.iterdir():
                try:
                    file_info = self._get_file_info(item)
                    files.append(file_info)
                except Exception as e:
                    logger.warning(f"Failed to get info for {item}: {e}")
                    continue

            return files

        except Exception as e:
            logger.error(f"Failed to list directory {dir_path}: {e}")
            return []

    async def get_directory_info(self, dir_path: str) -> DirectoryInfo | None:
        """Get comprehensive directory information."""
        try:
            if not self._is_safe_path(dir_path):
                return None

            path = Path(dir_path)
            if not path.exists() or not path.is_dir():
                return None

            files = await self.list_directory(dir_path)

            total_files = sum(1 for f in files if f.is_file)
            total_directories = sum(1 for f in files if f.is_directory)
            total_size = sum(f.size_bytes for f in files if f.is_file)

            stat = path.stat()

            return DirectoryInfo(
                path=str(path),
                name=path.name,
                total_files=total_files,
                total_directories=total_directories,
                total_size_bytes=total_size,
                created_at=datetime.fromtimestamp(stat.st_ctime),
                modified_at=datetime.fromtimestamp(stat.st_mtime),
                permissions=oct(stat.st_mode)[-3:],
                contents=[f.name for f in files],
            )

        except Exception as e:
            logger.error(f"Failed to get directory info for {dir_path}: {e}")
            return None

    async def search_files(
        self, query: str, directory: str = "", file_types: list[str] | None = None, max_results: int = 100
    ) -> list[FileInfo]:
        """Search for files by name or content."""
        try:
            search_dir = Path(directory) if directory else self.base_path

            if not self._is_safe_path(str(search_dir)):
                return []

            if not search_dir.exists() or not search_dir.is_dir():
                return []

            results: list[FileInfo] = []

            for root, dirs, files in os.walk(search_dir):
                for file in files:
                    if len(results) >= max_results:
                        break

                    file_path = Path(root) / file

                    # Check file type filter
                    if file_types and file_path.suffix.lower() not in file_types:
                        continue

                    # Check if filename matches query
                    if query.lower() in file_path.name.lower():
                        try:
                            file_info = self._get_file_info(file_path)
                            results.append(file_info)
                        except Exception as e:
                            logger.warning(f"Failed to get info for {file_path}: {e}")
                            continue

                if len(results) >= max_results:
                    break

            return results

        except Exception as e:
            logger.error(f"Failed to search files: {e}")
            return []


# Global instance
_filesystem_manager = FileSystemManager()


async def read_file(file_path: str) -> dict[str, Any]:
    """Read file content."""
    result = await _filesystem_manager.read_file(file_path)
    return {
        "success": result.success,
        "operation": result.operation,
        "source_path": result.source_path,
        "message": result.message,
        "error": result.error,
        "file_info": result.file_info.__dict__ if result.file_info else None,
    }


async def write_file(
    file_path: str, content: str, overwrite: bool = False, create_parents: bool = True
) -> dict[str, Any]:
    """Write content to file."""
    result = await _filesystem_manager.write_file(file_path, content, overwrite, create_parents)
    return {
        "success": result.success,
        "operation": result.operation,
        "source_path": result.source_path,
        "message": result.message,
        "error": result.error,
        "file_info": result.file_info.__dict__ if result.file_info else None,
    }


async def create_directory(dir_path: str, create_parents: bool = True) -> dict[str, Any]:
    """Create a directory."""
    result = await _filesystem_manager.create_directory(dir_path, create_parents)
    return {
        "success": result.success,
        "operation": result.operation,
        "source_path": result.source_path,
        "message": result.message,
        "error": result.error,
        "file_info": result.file_info.__dict__ if result.file_info else None,
    }


async def copy_file(source_path: str, target_path: str, overwrite: bool = False) -> dict[str, Any]:
    """Copy a file."""
    result = await _filesystem_manager.copy_file(source_path, target_path, overwrite)
    return {
        "success": result.success,
        "operation": result.operation,
        "source_path": result.source_path,
        "target_path": result.target_path,
        "message": result.message,
        "error": result.error,
        "file_info": result.file_info.__dict__ if result.file_info else None,
    }


async def move_file(source_path: str, target_path: str, overwrite: bool = False) -> dict[str, Any]:
    """Move a file."""
    result = await _filesystem_manager.move_file(source_path, target_path, overwrite)
    return {
        "success": result.success,
        "operation": result.operation,
        "source_path": result.source_path,
        "target_path": result.target_path,
        "message": result.message,
        "error": result.error,
        "file_info": result.file_info.__dict__ if result.file_info else None,
    }


async def delete_file(file_path: str) -> dict[str, Any]:
    """Delete a file or directory."""
    result = await _filesystem_manager.delete_file(file_path)
    return {
        "success": result.success,
        "operation": result.operation,
        "source_path": result.source_path,
        "message": result.message,
        "error": result.error,
    }


async def list_directory(dir_path: str = "") -> list[dict[str, Any]]:
    """List directory contents."""
    files = await _filesystem_manager.list_directory(dir_path)
    return [file.__dict__ for file in files]


async def get_directory_info(dir_path: str = "") -> dict[str, Any] | None:
    """Get directory information."""
    info = await _filesystem_manager.get_directory_info(dir_path)
    return info.__dict__ if info else None


async def search_files(
    query: str, directory: str = "", file_types: list[str] | None = None, max_results: int = 100
) -> list[dict[str, Any]]:
    """Search for files."""
    files = await _filesystem_manager.search_files(query, directory, file_types, max_results)
    return [file.__dict__ for file in files]


def register(mcp: Any) -> None:
    """Register the filesystem tools with the MCP server."""

    @mcp.tool()
    async def filesystem_read(file_path: str) -> str:
        """Read file content from the filesystem."""
        try:
            result = await read_file(file_path)
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            logger.error(f"Filesystem read failed: {e}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)

    @mcp.tool()
    async def filesystem_write(
        file_path: str, content: str, overwrite: bool = False, create_parents: bool = True
    ) -> str:
        """Write content to a file in the filesystem."""
        try:
            result = await write_file(file_path, content, overwrite, create_parents)
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            logger.error(f"Filesystem write failed: {e}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)

    @mcp.tool()
    async def filesystem_create_directory(dir_path: str, create_parents: bool = True) -> str:
        """Create a directory in the filesystem."""
        try:
            result = await create_directory(dir_path, create_parents)
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            logger.error(f"Filesystem create directory failed: {e}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)

    @mcp.tool()
    async def filesystem_copy(source_path: str, target_path: str, overwrite: bool = False) -> str:
        """Copy a file from source to target."""
        try:
            result = await copy_file(source_path, target_path, overwrite)
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            logger.error(f"Filesystem copy failed: {e}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)

    @mcp.tool()
    async def filesystem_move(source_path: str, target_path: str, overwrite: bool = False) -> str:
        """Move a file from source to target."""
        try:
            result = await move_file(source_path, target_path, overwrite)
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            logger.error(f"Filesystem move failed: {e}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)

    @mcp.tool()
    async def filesystem_delete(file_path: str) -> str:
        """Delete a file or directory."""
        try:
            result = await delete_file(file_path)
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            logger.error(f"Filesystem delete failed: {e}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)

    @mcp.tool()
    async def filesystem_list_directory(dir_path: str = "") -> str:
        """List contents of a directory."""
        try:
            files = await list_directory(dir_path)
            return json.dumps({"success": True, "files": files, "total_files": len(files)}, indent=2, default=str)
        except Exception as e:
            logger.error(f"Filesystem list directory failed: {e}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)

    @mcp.tool()
    async def filesystem_get_directory_info(dir_path: str = "") -> str:
        """Get comprehensive directory information."""
        try:
            info = await get_directory_info(dir_path)
            if info:
                return json.dumps({"success": True, "directory_info": info}, indent=2, default=str)
            else:
                return json.dumps({"success": False, "error": "Directory not found or not accessible"}, indent=2)
        except Exception as e:
            logger.error(f"Filesystem get directory info failed: {e}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)

    @mcp.tool()
    async def filesystem_search_files(
        query: str, directory: str = "", file_types: list[str] | None = None, max_results: int = 100
    ) -> str:
        """Search for files by name or content."""
        try:
            files = await search_files(query, directory, file_types, max_results)
            return json.dumps(
                {"success": True, "files": files, "total_found": len(files), "query": query}, indent=2, default=str
            )
        except Exception as e:
            logger.error(f"Filesystem search failed: {e}")
            return json.dumps({"success": False, "error": str(e)}, indent=2)
