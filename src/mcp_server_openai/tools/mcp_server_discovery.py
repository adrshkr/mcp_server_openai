"""
MCP Server Discovery and Health Monitoring Tool

This module provides comprehensive server discovery, health checks, and status monitoring
for all integrated MCP servers in the unified content creation system.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import httpx
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_TIMEOUT = 30.0
HEALTH_CHECK_INTERVAL = 60  # seconds
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 2  # seconds

# MCP Server configurations
MCP_SERVERS = {
    "sequential_thinking": {
        "name": "Sequential Thinking Server",
        "description": "AI-powered content planning and structuring",
        "endpoint": "/api/sequential-thinking/health",
        "required": True,
        "category": "planning",
    },
    "brave_search": {
        "name": "Brave Search Server",
        "description": "Web search and content research capabilities",
        "endpoint": "/api/brave-search/health",
        "required": False,
        "category": "research",
    },
    "memory": {
        "name": "Memory Server",
        "description": "Content storage and retrieval system",
        "endpoint": "/api/memory/health",
        "required": True,
        "category": "storage",
    },
    "filesystem": {
        "name": "Filesystem Server",
        "description": "File operations and management",
        "endpoint": "/api/filesystem/health",
        "required": True,
        "category": "storage",
    },
    "image_generation": {
        "name": "Image Generation Server",
        "description": "Multi-provider image generation (Unsplash, Stable Diffusion, Pixabay)",
        "endpoint": "/api/image-generation/health",
        "required": False,
        "category": "media",
    },
    "icon_generation": {
        "name": "Icon Generation Server",
        "description": "Multi-provider icon generation and management",
        "endpoint": "/api/icon-generation/health",
        "required": False,
        "category": "media",
    },
    "enhanced_ppt": {
        "name": "Enhanced PPT Generator",
        "description": "AI-powered PowerPoint presentation generation",
        "endpoint": "/api/enhanced-ppt/health",
        "required": True,
        "category": "generation",
    },
    "enhanced_document": {
        "name": "Enhanced Document Generator",
        "description": "Multi-format document generation (DOC, PDF, HTML)",
        "endpoint": "/api/enhanced-document/health",
        "required": True,
        "category": "generation",
    },
    "unified_content": {
        "name": "Unified Content Creator",
        "description": "Central orchestration tool for all content creation",
        "endpoint": "/api/unified-content/health",
        "required": True,
        "category": "orchestration",
    },
}


@dataclass
class ServerHealth:
    """Health status information for an MCP server."""

    server_id: str
    name: str
    status: str  # "healthy", "degraded", "unhealthy", "unknown"
    response_time: float
    last_check: datetime
    error_message: str | None = None
    version: str | None = None
    uptime: float | None = None
    memory_usage: float | None = None
    cpu_usage: float | None = None


@dataclass
class SystemStatus:
    """Overall system status and health information."""

    overall_status: str
    healthy_servers: int
    total_servers: int
    last_update: datetime
    servers: dict[str, ServerHealth] = field(default_factory=dict)
    system_metrics: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class DiscoveryRequest:
    """Request for server discovery and health check."""

    include_system_metrics: bool = True
    include_recommendations: bool = True
    timeout: float = DEFAULT_TIMEOUT


@dataclass
class DiscoveryResponse:
    """Response containing server discovery and health information."""

    status: str
    message: str
    system_status: SystemStatus
    timestamp: datetime = field(default_factory=datetime.now)


class MCPHealthChecker:
    """Health checker for MCP servers."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)
        self._health_cache: dict[str, ServerHealth] = {}
        self._last_system_check: datetime | None = None

    async def __aenter__(self) -> "MCPHealthChecker":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.client.aclose()

    async def check_server_health(self, server_id: str, config: dict[str, Any]) -> ServerHealth:
        """Check health of a specific MCP server."""
        endpoint = config["endpoint"]
        url = f"{self.base_url}{endpoint}"

        start_time = time.time()
        status = "unknown"
        error_message = None
        response_time = 0.0

        try:
            response = await self.client.get(url)
            response_time = time.time() - start_time

            if response.status_code == 200:  # HTTPStatus.OK
                status = "healthy"
                data = response.json()
                version = data.get("version")
                uptime = data.get("uptime")
                memory_usage = data.get("memory_usage")
                cpu_usage = data.get("cpu_usage")
            elif response.status_code == 503:  # HTTPStatus.SERVICE_UNAVAILABLE
                status = "degraded"
                error_message = "Service temporarily unavailable"
            else:
                status = "unhealthy"
                error_message = f"HTTP {response.status_code}: {response.text}"

        except httpx.TimeoutException:
            status = "unhealthy"
            error_message = "Request timeout"
            response_time = time.time() - start_time
        except httpx.HTTPError as e:
            status = "unhealthy"
            error_message = f"Request failed: {str(e)}"
            response_time = time.time() - start_time
        except Exception as e:
            status = "unhealthy"
            error_message = f"Unexpected error: {str(e)}"
            response_time = time.time() - start_time

        return ServerHealth(
            server_id=server_id,
            name=str(config["name"]),
            status=status,
            response_time=response_time,
            last_check=datetime.now(),
            error_message=error_message,
            version=locals().get("version"),
            uptime=locals().get("uptime"),
            memory_usage=locals().get("memory_usage"),
            cpu_usage=locals().get("cpu_usage"),
        )

    async def check_all_servers(self) -> dict[str, ServerHealth]:
        """Check health of all configured MCP servers."""
        tasks = []
        for server_id, config in MCP_SERVERS.items():
            task = self.check_server_health(server_id, config)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        server_health: dict[str, ServerHealth] = {}
        for i, (server_id, config) in enumerate(MCP_SERVERS.items()):
            if isinstance(results[i], Exception):
                server_health[server_id] = ServerHealth(
                    server_id=server_id,
                    name=str(config["name"]),
                    status="unhealthy",
                    response_time=0.0,
                    last_check=datetime.now(),
                    error_message=f"Health check failed: {str(results[i])}",
                )
            else:
                if isinstance(results[i], ServerHealth):
                    server_health[server_id] = results[i]

        self._health_cache = server_health
        return server_health

    def get_system_metrics(self) -> dict[str, Any]:
        """Get system-level metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_available": memory.available,
                "memory_total": memory.total,
                "disk_usage": disk.percent,
                "disk_free": disk.free,
                "disk_total": disk.total,
                "load_average": psutil.getloadavg() if hasattr(psutil, "getloadavg") else None,
                "uptime": time.time() - psutil.boot_time(),
            }
        except Exception as e:
            logger.warning(f"Failed to get system metrics: {e}")
            return {}

    def generate_recommendations(self, server_health: dict[str, ServerHealth]) -> list[str]:
        """Generate recommendations based on health status."""
        recommendations = []

        # Check for unhealthy required servers
        unhealthy_required = [
            server_id
            for server_id, health in server_health.items()
            if MCP_SERVERS[server_id]["required"] and health.status != "healthy"
        ]

        if unhealthy_required:
            recommendations.append(
                f"Critical: Required servers are unhealthy: {', '.join(unhealthy_required)}. "
                "System functionality may be limited."
            )

        # Check for degraded performance
        degraded_servers = [server_id for server_id, health in server_health.items() if health.status == "degraded"]

        if degraded_servers:
            recommendations.append(
                f"Warning: Servers experiencing degraded performance: {', '.join(degraded_servers)}. "
                "Consider investigating performance issues."
            )

        # Check response times
        slow_servers = [
            server_id
            for server_id, health in server_health.items()
            if health.response_time > 5.0  # More than 5 seconds
        ]

        if slow_servers:
            recommendations.append(
                f"Performance: Servers with slow response times: {', '.join(slow_servers)}. "
                "Consider optimization or scaling."
            )

        # Check system resources
        system_metrics = self.get_system_metrics()
        if system_metrics:
            if system_metrics.get("cpu_usage", 0) > 80:
                recommendations.append("System: High CPU usage detected. Consider scaling or optimization.")

            if system_metrics.get("memory_usage", 0) > 85:
                recommendations.append("System: High memory usage detected. Consider memory optimization or scaling.")

        if not recommendations:
            recommendations.append("All systems operating normally.")

        return recommendations

    async def get_system_status(self, request: DiscoveryRequest) -> SystemStatus:
        """Get comprehensive system status."""
        # Check if we have recent health data
        if self._last_system_check and datetime.now() - self._last_system_check < timedelta(
            seconds=HEALTH_CHECK_INTERVAL
        ):
            server_health = self._health_cache
        else:
            server_health = await self.check_all_servers()
            self._last_system_check = datetime.now()

        # Calculate overall status
        total_servers = len(server_health)
        healthy_servers = sum(1 for h in server_health.values() if h.status == "healthy")

        if healthy_servers == total_servers:
            overall_status = "healthy"
        elif healthy_servers >= total_servers * 0.8:  # 80% healthy
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        # Get system metrics if requested
        system_metrics = {}
        if request.include_system_metrics:
            system_metrics = self.get_system_metrics()

        # Generate recommendations if requested
        recommendations = []
        if request.include_recommendations:
            recommendations = self.generate_recommendations(server_health)

        return SystemStatus(
            overall_status=overall_status,
            healthy_servers=healthy_servers,
            total_servers=total_servers,
            last_update=datetime.now(),
            servers=server_health,
            system_metrics=system_metrics,
            recommendations=recommendations,
        )


class MCPServerDiscovery:
    """Main MCP Server Discovery tool."""

    def __init__(self) -> None:
        self.health_checker = MCPHealthChecker()
        self.discovery_history: list[DiscoveryResponse] = []

    async def discover_servers(self, request: DiscoveryRequest) -> DiscoveryResponse:
        """Discover and check health of all MCP servers."""
        try:
            async with self.health_checker:
                system_status = await self.health_checker.get_system_status(request)

            # Determine response status and message
            if system_status.overall_status == "healthy":
                status = "success"
                message = f"All {system_status.total_servers} MCP servers are healthy"
            elif system_status.overall_status == "degraded":
                status = "partial_success"
                message = f"{system_status.healthy_servers}/{system_status.total_servers} MCP servers are healthy"
            else:
                status = "error"
                message = f"System health check failed: {system_status.healthy_servers}/{system_status.total_servers} servers healthy"

            response = DiscoveryResponse(status=status, message=message, system_status=system_status)

            # Store in history (keep last 100)
            self.discovery_history.append(response)
            if len(self.discovery_history) > 100:
                self.discovery_history = self.discovery_history[-100:]

            return response

        except Exception as e:
            logger.error(f"Server discovery failed: {e}")
            return DiscoveryResponse(
                status="error",
                message=f"Server discovery failed: {str(e)}",
                system_status=SystemStatus(
                    overall_status="unknown",
                    healthy_servers=0,
                    total_servers=len(MCP_SERVERS),
                    last_update=datetime.now(),
                ),
            )

    async def get_server_info(self, server_id: str) -> dict[str, Any] | None:
        """Get detailed information about a specific server."""
        if server_id not in MCP_SERVERS:
            return None

        config = MCP_SERVERS[server_id]

        # Get current health status
        async with self.health_checker:
            server_health = await self.health_checker.check_server_health(server_id, config)

        return {
            "server_id": server_id,
            "config": config,
            "health": {
                "status": server_health.status,
                "response_time": server_health.response_time,
                "last_check": server_health.last_check.isoformat(),
                "error_message": server_health.error_message,
                "version": server_health.version,
                "uptime": server_health.uptime,
                "memory_usage": server_health.memory_usage,
                "cpu_usage": server_health.cpu_usage,
            },
        }

    async def get_discovery_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get discovery history for monitoring and analysis."""
        history = []
        for response in self.discovery_history[-limit:]:
            history.append(
                {
                    "timestamp": response.timestamp.isoformat(),
                    "status": response.status,
                    "message": response.message,
                    "overall_status": response.system_status.overall_status,
                    "healthy_servers": response.system_status.healthy_servers,
                    "total_servers": response.system_status.total_servers,
                }
            )
        return history

    def get_available_servers(self) -> dict[str, dict[str, Any]]:
        """Get list of all available MCP servers."""
        return MCP_SERVERS.copy()


# Global instance
discovery_tool = MCPServerDiscovery()


async def discover_mcp_servers(
    include_system_metrics: bool = True, include_recommendations: bool = True, timeout: float = DEFAULT_TIMEOUT
) -> dict[str, Any]:
    """
    Discover and check health of all MCP servers.

    Args:
        include_system_metrics: Whether to include system-level metrics
        include_recommendations: Whether to include health recommendations
        timeout: Request timeout in seconds

    Returns:
        Dictionary containing discovery results and system status
    """
    request = DiscoveryRequest(
        include_system_metrics=include_system_metrics, include_recommendations=include_recommendations, timeout=timeout
    )

    response = await discovery_tool.discover_servers(request)

    return {
        "status": response.status,
        "message": response.message,
        "timestamp": response.timestamp.isoformat(),
        "system_status": {
            "overall_status": response.system_status.overall_status,
            "healthy_servers": response.system_status.healthy_servers,
            "total_servers": response.system_status.total_servers,
            "last_update": response.system_status.last_update.isoformat(),
            "servers": {
                server_id: {
                    "name": health.name,
                    "status": health.status,
                    "response_time": health.response_time,
                    "last_check": health.last_check.isoformat(),
                    "error_message": health.error_message,
                    "version": health.version,
                    "uptime": health.uptime,
                    "memory_usage": health.memory_usage,
                    "cpu_usage": health.cpu_usage,
                }
                for server_id, health in response.system_status.servers.items()
            },
            "system_metrics": response.system_status.system_metrics,
            "recommendations": response.system_status.recommendations,
        },
    }


async def get_server_info(server_id: str) -> dict[str, Any] | None:
    """
    Get detailed information about a specific MCP server.

    Args:
        server_id: Identifier of the server to query

    Returns:
        Dictionary containing server information and health status, or None if not found
    """
    return await discovery_tool.get_server_info(server_id)


async def get_discovery_history(limit: int = 50) -> list[dict[str, Any]]:
    """
    Get discovery history for monitoring and analysis.

    Args:
        limit: Maximum number of history entries to return

    Returns:
        List of discovery history entries
    """
    return await discovery_tool.get_discovery_history(limit)


def get_available_servers() -> dict[str, dict[str, Any]]:
    """
    Get list of all available MCP servers.

    Returns:
        Dictionary mapping server IDs to their configurations
    """
    return discovery_tool.get_available_servers()


def register(server: Any) -> None:
    """Register MCP tools with the server."""

    @server.tool()
    async def mcp_server_discovery_discover(
        include_system_metrics: bool = True, include_recommendations: bool = True, timeout: float = DEFAULT_TIMEOUT
    ) -> dict[str, Any]:
        """
        Discover and check health of all MCP servers.

        This tool provides comprehensive health monitoring and status information
        for all integrated MCP servers in the unified content creation system.

        Args:
            include_system_metrics: Include system-level metrics (CPU, memory, disk)
            include_recommendations: Include health recommendations and alerts
            timeout: Request timeout in seconds

        Returns:
            Complete system status with server health information
        """
        return await discover_mcp_servers(
            include_system_metrics=include_system_metrics,
            include_recommendations=include_recommendations,
            timeout=timeout,
        )

    @server.tool()
    async def mcp_server_discovery_server_info(server_id: str) -> dict[str, Any] | None:
        """
        Get detailed information about a specific MCP server.

        Args:
            server_id: Identifier of the server to query

        Returns:
            Server information and health status
        """
        return await get_server_info(server_id)

    @server.tool()
    async def mcp_server_discovery_history(limit: int = 50) -> list[dict[str, Any]]:
        """
        Get discovery history for monitoring and analysis.

        Args:
            limit: Maximum number of history entries to return

        Returns:
            List of discovery history entries
        """
        return await get_discovery_history(limit)

    @server.tool()
    def mcp_server_discovery_servers() -> dict[str, dict[str, Any]]:
        """
        Get list of all available MCP servers.

        Returns:
            Dictionary mapping server IDs to their configurations
        """
        return get_available_servers()


if __name__ == "__main__":
    # Demo and testing
    async def main() -> None:
        print("MCP Server Discovery Tool Demo")
        print("=" * 40)

        # Get available servers
        servers = get_available_servers()
        print(f"Available servers: {len(servers)}")
        for server_id, config in servers.items():
            print(f"  - {server_id}: {config['name']}")

        print("\nRunning health check...")

        # Discover servers
        result = await discover_mcp_servers()
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"Overall: {result['system_status']['overall_status']}")
        print(f"Healthy: {result['system_status']['healthy_servers']}/{result['system_status']['total_servers']}")

        # Show server details
        print("\nServer Details:")
        for server_id, health in result["system_status"]["servers"].items():
            print(f"  {server_id}: {health['status']} ({health['response_time']:.2f}s)")

        # Show recommendations
        if result["system_status"]["recommendations"]:
            print("\nRecommendations:")
            for rec in result["system_status"]["recommendations"]:
                print(f"  - {rec}")

    asyncio.run(main())
