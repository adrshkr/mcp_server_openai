"""
MCP Memory Server Implementation

This server provides content storage and retrieval capabilities for the unified content creator system.
It supports storing and retrieving various types of content including presentations, documents, and metadata.
"""

import asyncio
import hashlib
import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_DB_PATH = "data/memory.db"
DEFAULT_MAX_ITEMS = 10000
DEFAULT_CLEANUP_INTERVAL = 3600  # 1 hour
DEFAULT_RETENTION_DAYS = 30


@dataclass
class MemoryItem:
    """Represents a memory item stored in the system."""

    id: str
    content_type: str  # presentation, document, html, pdf, analysis, plan
    title: str
    content: str
    metadata: dict[str, Any]
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    size_bytes: int = 0
    hash: str = ""
    client_id: str | None = None
    expires_at: datetime | None = None


@dataclass
class MemoryQuery:
    """Query for searching memory items."""

    query: str
    content_type: str | None = None
    tags: list[str] | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    max_results: int = 50
    sort_by: str = "relevance"  # relevance, date, access_count
    client_id: str | None = None


@dataclass
class MemoryResponse:
    """Response from memory operations."""

    status: str
    items: list[MemoryItem]
    total_found: int
    query_time: float
    client_id: str | None = None
    error: str | None = None


class MemoryDatabase:
    """SQLite-based memory storage system."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create memory items table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS memory_items (
                        id TEXT PRIMARY KEY,
                        content_type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        metadata TEXT NOT NULL,
                        tags TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        access_count INTEGER DEFAULT 0,
                        last_accessed TEXT NOT NULL,
                        size_bytes INTEGER DEFAULT 0,
                        hash TEXT NOT NULL,
                        client_id TEXT,
                        expires_at TEXT
                    )
                """
                )

                # Create indexes for better performance
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_content_type ON memory_items(content_type)
                """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_tags ON memory_items(tags)
                """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_created_at ON memory_items(created_at)
                """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_client_id ON memory_items(client_id)
                """
                )

                conn.commit()
                logger.info("Memory database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize memory database: {e}")
            raise

    def _serialize_metadata(self, metadata: dict[str, Any]) -> str:
        """Serialize metadata dictionary to JSON string."""
        return json.dumps(metadata, default=str)

    def _deserialize_metadata(self, metadata_str: str) -> dict[str, Any]:
        """Deserialize JSON string back to metadata dictionary."""
        try:
            result = json.loads(metadata_str)
            if isinstance(result, dict):
                return result
            else:
                return {}
        except json.JSONDecodeError:
            return {}

    def _serialize_tags(self, tags: list[str]) -> str:
        """Serialize tags list to JSON string."""
        return json.dumps(tags)

    def _deserialize_tags(self, tags_str: str) -> list[str]:
        """Deserialize JSON string back to tags list."""
        try:
            result = json.loads(tags_str)
            if isinstance(result, list):
                return result
            else:
                return []
        except json.JSONDecodeError:
            return []

    def _datetime_to_str(self, dt: datetime) -> str:
        """Convert datetime to ISO string."""
        return dt.isoformat()

    def _str_to_datetime(self, dt_str: str) -> datetime:
        """Convert ISO string back to datetime."""
        try:
            return datetime.fromisoformat(dt_str)
        except ValueError:
            return datetime.utcnow()

    async def store_item(self, item: MemoryItem) -> bool:
        """Store a memory item in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO memory_items 
                    (id, content_type, title, content, metadata, tags, created_at, updated_at, 
                     access_count, last_accessed, size_bytes, hash, client_id, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        item.id,
                        item.content_type,
                        item.title,
                        item.content,
                        self._serialize_metadata(item.metadata),
                        self._serialize_tags(item.tags),
                        self._datetime_to_str(item.created_at),
                        self._datetime_to_str(item.updated_at),
                        item.access_count,
                        self._datetime_to_str(item.last_accessed),
                        item.size_bytes,
                        item.hash,
                        item.client_id,
                        self._datetime_to_str(item.expires_at) if item.expires_at else None,
                    ),
                )

                conn.commit()
                logger.info(f"Stored memory item: {item.id}")
                return True

        except Exception as e:
            logger.error(f"Failed to store memory item: {e}")
            return False

    async def retrieve_item(self, item_id: str) -> MemoryItem | None:
        """Retrieve a memory item by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM memory_items WHERE id = ?
                """,
                    (item_id,),
                )

                row = cursor.fetchone()
                if row:
                    # Update access count and last accessed
                    cursor.execute(
                        """
                        UPDATE memory_items 
                        SET access_count = access_count + 1, last_accessed = ?
                        WHERE id = ?
                    """,
                        (self._datetime_to_str(datetime.utcnow()), item_id),
                    )
                    conn.commit()

                    return self._row_to_memory_item(row)

                return None

        except Exception as e:
            logger.error(f"Failed to retrieve memory item: {e}")
            return None

    async def search_items(self, query: MemoryQuery) -> list[MemoryItem]:
        """Search memory items based on query criteria."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Build search query
                sql_parts = ["SELECT * FROM memory_items WHERE 1=1"]
                params = []

                if query.content_type:
                    sql_parts.append("AND content_type = ?")
                    params.append(query.content_type)

                if query.client_id:
                    sql_parts.append("AND client_id = ?")
                    params.append(query.client_id)

                if query.date_from:
                    sql_parts.append("AND created_at >= ?")
                    params.append(self._datetime_to_str(query.date_from))

                if query.date_to:
                    sql_parts.append("AND created_at <= ?")
                    params.append(self._datetime_to_str(query.date_to))

                # Add text search
                if query.query:
                    sql_parts.append("AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)")
                    search_term = f"%{query.query}%"
                    params.extend([search_term, search_term, search_term])

                # Add tag filtering
                if query.tags:
                    tag_conditions = []
                    for tag in query.tags:
                        tag_conditions.append("tags LIKE ?")
                        params.append(f"%{tag}%")
                    sql_parts.append(f"AND ({' OR '.join(tag_conditions)})")

                # Add sorting
                if query.sort_by == "date":
                    sql_parts.append("ORDER BY created_at DESC")
                elif query.sort_by == "access_count":
                    sql_parts.append("ORDER BY access_count DESC")
                else:  # relevance - default
                    sql_parts.append("ORDER BY access_count DESC, created_at DESC")

                # Add limit
                sql_parts.append(f"LIMIT {query.max_results}")

                sql = " ".join(sql_parts)
                cursor.execute(sql, params)

                rows = cursor.fetchall()
                return [self._row_to_memory_item(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to search memory items: {e}")
            return []

    def _row_to_memory_item(self, row: tuple) -> MemoryItem:
        """Convert database row to MemoryItem object."""
        return MemoryItem(
            id=row[0],
            content_type=row[1],
            title=row[2],
            content=row[3],
            metadata=self._deserialize_metadata(row[4]),
            tags=self._deserialize_tags(row[5]),
            created_at=self._str_to_datetime(row[6]),
            updated_at=self._str_to_datetime(row[7]),
            access_count=row[8],
            last_accessed=self._str_to_datetime(row[9]),
            size_bytes=row[10],
            hash=row[11],
            client_id=row[12],
            expires_at=self._str_to_datetime(row[13]) if row[13] else None,
        )

    async def delete_item(self, item_id: str) -> bool:
        """Delete a memory item by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("DELETE FROM memory_items WHERE id = ?", (item_id,))
                conn.commit()

                if cursor.rowcount > 0:
                    logger.info(f"Deleted memory item: {item_id}")
                    return True
                else:
                    logger.warning(f"Memory item not found: {item_id}")
                    return False

        except Exception as e:
            logger.error(f"Failed to delete memory item: {e}")
            return False

    async def cleanup_expired_items(self) -> int:
        """Remove expired memory items."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    DELETE FROM memory_items 
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                """,
                    (self._datetime_to_str(datetime.utcnow()),),
                )

                deleted_count = cursor.rowcount
                conn.commit()

                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired memory items")

                return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup expired items: {e}")
            return 0


class MemoryServer:
    """Main memory server that provides content storage and retrieval capabilities."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.database = MemoryDatabase(db_path)
        self.cleanup_task: asyncio.Task | None = None
        self._start_cleanup_task()

    def _start_cleanup_task(self) -> None:
        """Start the background cleanup task."""

        async def cleanup_loop() -> None:
            while True:
                try:
                    await asyncio.sleep(DEFAULT_CLEANUP_INTERVAL)
                    await self.database.cleanup_expired_items()
                except Exception as e:
                    logger.error(f"Cleanup task error: {e}")

        self.cleanup_task = asyncio.create_task(cleanup_loop())

    async def store_content(
        self,
        content_type: str,
        title: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        client_id: str | None = None,
        ttl_days: int | None = None,
    ) -> str:
        """Store content in memory."""
        try:
            # Generate unique ID
            item_id = str(uuid.uuid4())

            # Calculate content hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()

            # Calculate size
            size_bytes = len(content.encode("utf-8"))

            # Set expiration if TTL specified
            expires_at = None
            if ttl_days:
                expires_at = datetime.utcnow() + timedelta(days=ttl_days)

            # Create memory item
            item = MemoryItem(
                id=item_id,
                content_type=content_type,
                title=title,
                content=content,
                metadata=metadata or {},
                tags=tags or [],
                expires_at=expires_at,
                size_bytes=size_bytes,
                hash=content_hash,
                client_id=client_id,
            )

            # Store in database
            success = await self.database.store_item(item)
            if success:
                return item_id
            else:
                raise Exception("Failed to store content in database")

        except Exception as e:
            logger.error(f"Failed to store content: {e}")
            raise

    async def retrieve_content(self, item_id: str) -> MemoryItem | None:
        """Retrieve content by ID."""
        try:
            return await self.database.retrieve_item(item_id)
        except Exception as e:
            logger.error(f"Failed to retrieve content: {e}")
            return None

    async def search_content(
        self,
        query: str,
        content_type: str | None = None,
        tags: list[str] | None = None,
        max_results: int = 50,
        client_id: str | None = None,
    ) -> list[MemoryItem]:
        """Search content based on query and filters."""
        try:
            memory_query = MemoryQuery(
                query=query, content_type=content_type, tags=tags, max_results=max_results, client_id=client_id
            )

            return await self.database.search_items(memory_query)
        except Exception as e:
            logger.error(f"Failed to search content: {e}")
            return []

    async def delete_content(self, item_id: str) -> bool:
        """Delete content by ID."""
        try:
            return await self.database.delete_item(item_id)
        except Exception as e:
            logger.error(f"Failed to delete content: {e}")
            return False

    async def get_content_stats(self, client_id: str | None = None) -> dict[str, Any]:
        """Get content statistics."""
        try:
            with sqlite3.connect(self.database.db_path) as conn:
                cursor = conn.cursor()

                # Count total items
                if client_id:
                    cursor.execute("SELECT COUNT(*) FROM memory_items WHERE client_id = ?", (client_id,))
                else:
                    cursor.execute("SELECT COUNT(*) FROM memory_items")
                total_items = cursor.fetchone()[0]

                # Count by content type
                if client_id:
                    cursor.execute(
                        """
                        SELECT content_type, COUNT(*) 
                        FROM memory_items 
                        WHERE client_id = ? 
                        GROUP BY content_type
                    """,
                        (client_id,),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT content_type, COUNT(*) 
                        FROM memory_items 
                        GROUP BY content_type
                    """
                    )
                type_counts = dict(cursor.fetchall())

                # Calculate total size
                if client_id:
                    cursor.execute("SELECT SUM(size_bytes) FROM memory_items WHERE client_id = ?", (client_id,))
                else:
                    cursor.execute("SELECT SUM(size_bytes) FROM memory_items")
                total_size = cursor.fetchone()[0] or 0

                return {
                    "total_items": total_items,
                    "type_counts": type_counts,
                    "total_size_bytes": total_size,
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "client_id": client_id,
                }

        except Exception as e:
            logger.error(f"Failed to get content stats: {e}")
            return {"error": str(e)}


# Global instance
_memory_server = MemoryServer()


async def store_content(
    content_type: str,
    title: str,
    content: str,
    metadata: dict[str, Any] | None = None,
    tags: list[str] | None = None,
    client_id: str | None = None,
    ttl_days: int | None = None,
) -> str:
    """Store content in memory system."""
    return await _memory_server.store_content(
        content_type=content_type,
        title=title,
        content=content,
        metadata=metadata,
        tags=tags,
        client_id=client_id,
        ttl_days=ttl_days,
    )


async def retrieve_content(item_id: str) -> dict[str, Any] | None:
    """Retrieve content from memory system."""
    item = await _memory_server.retrieve_content(item_id)
    if item:
        return {
            "id": item.id,
            "content_type": item.content_type,
            "title": item.title,
            "content": item.content,
            "metadata": item.metadata,
            "tags": item.tags,
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat(),
            "access_count": item.access_count,
            "size_bytes": item.size_bytes,
            "client_id": item.client_id,
        }
    return None


async def search_content(
    query: str,
    content_type: str | None = None,
    tags: list[str] | None = None,
    max_results: int = 50,
    client_id: str | None = None,
) -> list[dict[str, Any]]:
    """Search content in memory system."""
    items = await _memory_server.search_content(
        query=query, content_type=content_type, tags=tags, max_results=max_results, client_id=client_id
    )

    return [
        {
            "id": item.id,
            "content_type": item.content_type,
            "title": item.title,
            "content": item.content[:200] + "..." if len(item.content) > 200 else item.content,
            "metadata": item.metadata,
            "tags": item.tags,
            "created_at": item.created_at.isoformat(),
            "access_count": item.access_count,
            "relevance_score": min(1.0, item.access_count / 10.0),  # Simple relevance scoring
        }
        for item in items
    ]


async def delete_content(item_id: str) -> bool:
    """Delete content from memory system."""
    return await _memory_server.delete_content(item_id)


async def get_memory_stats(client_id: str | None = None) -> dict[str, Any]:
    """Get memory system statistics."""
    return await _memory_server.get_content_stats(client_id)


def register(mcp: Any) -> None:
    """Register the memory tools with the MCP server."""

    @mcp.tool()
    async def memory_store(
        content_type: str,
        title: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        client_id: str | None = None,
        ttl_days: int | None = None,
    ) -> str:
        """Store content in the memory system for later retrieval."""
        try:
            item_id = await store_content(
                content_type=content_type,
                title=title,
                content=content,
                metadata=metadata,
                tags=tags,
                client_id=client_id,
                ttl_days=ttl_days,
            )

            return json.dumps(
                {"status": "success", "item_id": item_id, "message": f"Content stored successfully with ID: {item_id}"},
                indent=2,
            )

        except Exception as e:
            logger.error(f"Memory store failed: {e}")
            return json.dumps({"status": "error", "error": str(e), "client_id": client_id}, indent=2)

    @mcp.tool()
    async def memory_retrieve(item_id: str, client_id: str | None = None) -> str:
        """Retrieve content from the memory system by ID."""
        try:
            content = await retrieve_content(item_id)

            if content:
                return json.dumps({"status": "success", "content": content}, indent=2)
            else:
                return json.dumps(
                    {"status": "not_found", "message": f"Content with ID {item_id} not found", "client_id": client_id},
                    indent=2,
                )

        except Exception as e:
            logger.error(f"Memory retrieve failed: {e}")
            return json.dumps({"status": "error", "error": str(e), "client_id": client_id}, indent=2)

    @mcp.tool()
    async def memory_search(
        query: str,
        content_type: str | None = None,
        tags: list[str] | None = None,
        max_results: int = 50,
        client_id: str | None = None,
    ) -> str:
        """Search for content in the memory system."""
        try:
            results = await search_content(
                query=query, content_type=content_type, tags=tags, max_results=max_results, client_id=client_id
            )

            return json.dumps(
                {"status": "success", "results": results, "total_found": len(results), "query": query}, indent=2
            )

        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return json.dumps({"status": "error", "error": str(e), "client_id": client_id}, indent=2)

    @mcp.tool()
    async def memory_delete(item_id: str, client_id: str | None = None) -> str:
        """Delete content from the memory system."""
        try:
            success = await delete_content(item_id)

            if success:
                return json.dumps(
                    {"status": "success", "message": f"Content with ID {item_id} deleted successfully"}, indent=2
                )
            else:
                return json.dumps(
                    {"status": "not_found", "message": f"Content with ID {item_id} not found", "client_id": client_id},
                    indent=2,
                )

        except Exception as e:
            logger.error(f"Memory delete failed: {e}")
            return json.dumps({"status": "error", "error": str(e), "client_id": client_id}, indent=2)

    @mcp.tool()
    async def memory_stats(client_id: str | None = None) -> str:
        """Get memory system statistics."""
        try:
            stats = await get_memory_stats(client_id)

            return json.dumps({"status": "success", "stats": stats}, indent=2)

        except Exception as e:
            logger.error(f"Memory stats failed: {e}")
            return json.dumps({"status": "error", "error": str(e), "client_id": client_id}, indent=2)
