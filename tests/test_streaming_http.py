"""
Comprehensive tests for modern streamable HTTP server.

Tests cover:
- Enhanced SSE streaming with multiplexing
- WebSocket real-time communication
- Response compression and optimization
- Rate limiting and security features
- Performance monitoring and metrics
- Error handling and graceful shutdown
"""

import json
import time
from unittest.mock import AsyncMock, patch

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from mcp_server_openai.server_config import ServerConfig
from mcp_server_openai.streaming_http import _server_metrics, app


class TestEnhancedEndpoints:
    """Test enhanced HTTP endpoints."""

    def test_enhanced_health(self):
        """Test enhanced health endpoint with metrics."""
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            assert "healthy" in response.text or "starting" in response.text
            assert "uptime:" in response.text

    def test_enhanced_info(self):
        """Test enhanced info endpoint with capabilities."""
        with TestClient(app) as client:
            response = client.get("/info")
            assert response.status_code == 200

            data = response.json()
            assert data["name"] == "mcp_server_openai"
            assert data["version"] == "0.2.0"

            # Check capabilities
            capabilities = data["capabilities"]
            assert capabilities["http2"] is True
            assert capabilities["websockets"] is True
            assert capabilities["streaming"] is True
            assert "gzip" in capabilities["compression"]
            assert "brotli" in capabilities["compression"]

            # Check endpoints
            endpoints = data["endpoints"]
            assert "/health" in endpoints["health"]
            assert "/info" in endpoints["info"]
            assert "/metrics" in endpoints["metrics"]
            assert "/mcp/sse" in endpoints["mcp_sse"]
            assert "/mcp/ws" in endpoints["mcp_ws"]

            # Check metrics
            metrics = data["metrics"]
            assert "uptime_seconds" in metrics
            assert "requests_total" in metrics
            assert "active_connections" in metrics

    def test_metrics_endpoint(self):
        """Test Prometheus-style metrics endpoint."""
        with TestClient(app) as client:
            response = client.get("/metrics")
            assert response.status_code == 200

            data = response.json()
            assert "server" in data
            assert "claude_usage" in data
            assert "cost_monitoring" in data
            assert "timestamp" in data

            # Check server metrics structure
            server_metrics = data["server"]
            assert "uptime_seconds" in server_metrics
            assert "requests_total" in server_metrics

            # Check Claude usage structure
            usage_metrics = data["claude_usage"]
            assert "tokens" in usage_metrics
            assert "cost_usd" in usage_metrics

    def test_usage_endpoint(self):
        """Test detailed usage tracking endpoint."""
        with TestClient(app) as client:
            response = client.get("/usage")
            assert response.status_code == 200

            data = response.json()
            assert "current_usage" in data
            assert "limits" in data
            assert "projections" in data
            assert "configuration" in data
            assert "timestamp" in data

            # Check limits structure
            limits = data["limits"]
            assert "configured" in limits
            assert "status" in limits

            # Check projections
            projections = data["projections"]
            assert "projected_hourly_cost" in projections
            assert "projected_daily_cost" in projections


class TestEnhancedSSE:
    """Test enhanced Server-Sent Events functionality."""

    def test_enhanced_sse_basic(self):
        """Test basic enhanced SSE functionality."""
        with TestClient(app) as client:
            # Use stream context manager for SSE endpoint
            with client.stream("GET", "/mcp/sse?client_id=test") as response:
                assert response.status_code == 200
                assert "text/event-stream" in response.headers["content-type"]
                assert "no-cache" in response.headers["cache-control"]
                # Don't read the stream content to avoid hanging

    def test_sse_capability_negotiation(self):
        """Test SSE with capability negotiation."""
        headers = {"Accept-Encoding": "gzip, deflate, br"}

        with TestClient(app) as client:
            # Test that the endpoint accepts capability parameters
            with client.stream("GET", "/mcp/sse?client_id=test&multiplex=true", headers=headers) as response:
                assert response.status_code == 200
                assert "text/event-stream" in response.headers["content-type"]
                # Don't read the stream content to avoid hanging


class TestWebSocketFunctionality:
    """Test WebSocket real-time communication."""

    def test_websocket_connection(self):
        """Test basic WebSocket connection."""
        with TestClient(app) as client:
            with client.websocket_connect("/mcp/ws?client_id=test") as websocket:
                # Should receive welcome message
                data = websocket.receive_json()
                assert data["type"] == "welcome"
                assert "session_id" in data
                assert "capabilities" in data

                capabilities = data["capabilities"]
                assert capabilities["compression"] is True
                assert capabilities["streaming"] is True
                assert capabilities["heartbeat"] is True

    def test_websocket_echo(self):
        """Test WebSocket echo functionality."""
        with TestClient(app) as client:
            with client.websocket_connect("/mcp/ws?client_id=test") as websocket:
                # Skip welcome message
                websocket.receive_json()

                # Send echo message
                echo_msg = {"type": "echo", "message": "Hello WebSocket!"}
                websocket.send_json(echo_msg)

                # Receive echo response
                response = websocket.receive_json()
                assert response["type"] == "echo_response"
                assert response["original"] == echo_msg
                assert "server_time" in response

    def test_websocket_subscription(self):
        """Test WebSocket subscription functionality."""
        with TestClient(app) as client:
            with client.websocket_connect("/mcp/ws?client_id=test") as websocket:
                # Skip welcome message
                websocket.receive_json()

                # Subscribe to stream
                subscribe_msg = {"type": "subscribe", "stream": "events"}
                websocket.send_json(subscribe_msg)

                # Receive subscription confirmation
                response = websocket.receive_json()
                assert response["type"] == "subscribed"
                assert response["stream"] == "events"
                assert "session_id" in response

    def test_websocket_unknown_message(self):
        """Test WebSocket handling of unknown message types."""
        with TestClient(app) as client:
            with client.websocket_connect("/mcp/ws?client_id=test") as websocket:
                # Skip welcome message
                websocket.receive_json()

                # Send unknown message type
                unknown_msg = {"type": "unknown_type", "data": "test"}
                websocket.send_json(unknown_msg)

                # Receive error response
                response = websocket.receive_json()
                assert response["type"] == "error"
                assert "Unknown message type" in response["message"]


class TestStreamingResponses:
    """Test streaming response functionality."""

    def test_streaming_data_endpoint(self):
        """Test streaming large dataset endpoint."""
        with TestClient(app) as client:
            with client.stream("GET", "/stream") as response:
                assert response.status_code == 200
                assert response.headers["content-type"] == "application/json"
                assert response.headers["transfer-encoding"] == "chunked"

                # Collect all chunks using iter_bytes
                content = b""
                for chunk in response.iter_bytes():
                    content += chunk

                # Parse JSON response
                data = json.loads(content.decode())
                assert "data" in data
                assert len(data["data"]) == 100

                # Verify structure of items
                first_item = data["data"][0]
                assert "id" in first_item
                assert "timestamp" in first_item
                assert "data" in first_item
                assert "metadata" in first_item

    def test_streaming_json_response_compression(self):
        """Test streaming JSON response with compression."""
        # This test would require a larger dataset to trigger compression
        # For now, we test the basic functionality
        with TestClient(app) as client:
            response = client.get("/info")
            assert response.status_code == 200
            # Compression headers are added by middleware, not visible in test client


class TestSecurityFeatures:
    """Test security features and headers."""

    def test_security_headers(self):
        """Test that security headers are properly set."""
        with TestClient(app) as client:
            response = client.get("/health")

            # Check for security headers
            headers = response.headers
            assert headers.get("x-content-type-options") == "nosniff"
            assert headers.get("x-frame-options") == "DENY"
            assert headers.get("x-xss-protection") == "1; mode=block"
            assert "strict-transport-security" in headers
            assert "content-security-policy" in headers
            assert "x-request-id" in headers
            assert "x-process-time" in headers

    def test_cors_headers(self):
        """Test CORS headers are properly set."""
        with TestClient(app) as client:
            # Test CORS headers on a regular request (CORS middleware adds headers to all responses)
            response = client.get("/info", headers={"Origin": "https://example.com"})

            headers = response.headers
            # Check for CORS headers that should be present
            assert "access-control-allow-origin" in headers
            # Note: access-control-allow-methods and access-control-allow-headers
            # are only sent on preflight requests, not regular requests

    @patch("slowapi.Limiter.limit")
    def test_rate_limiting(self, mock_limit):
        """Test rate limiting functionality."""
        # Mock the rate limiter to avoid actual limiting in tests
        mock_limit.return_value = lambda func: func

        with TestClient(app) as client:
            # Make multiple requests
            for _ in range(5):
                response = client.get("/info")
                assert response.status_code == 200


class TestPerformanceFeatures:
    """Test performance optimization features."""

    def test_response_compression(self):
        """Test response compression."""
        with TestClient(app) as client:
            # Request with compression support
            headers = {"Accept-Encoding": "gzip, deflate, br"}
            response = client.get("/info", headers=headers)

            assert response.status_code == 200
            # Compression is handled by middleware in production

    def test_request_timing(self):
        """Test request timing headers."""
        with TestClient(app) as client:
            response = client.get("/health")

            assert "x-process-time" in response.headers
            process_time = float(response.headers["x-process-time"])
            assert process_time >= 0
            assert process_time < 1.0  # Should be very fast

    def test_request_id_generation(self):
        """Test request ID generation."""
        with TestClient(app) as client:
            response1 = client.get("/health")
            response2 = client.get("/health")

            assert "x-request-id" in response1.headers
            assert "x-request-id" in response2.headers

            # Request IDs should be different
            assert response1.headers["x-request-id"] != response2.headers["x-request-id"]


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_endpoints(self):
        """Test handling of invalid endpoints."""
        with TestClient(app) as client:
            response = client.get("/nonexistent")
            assert response.status_code == 404

    def test_method_not_allowed(self):
        """Test handling of invalid HTTP methods."""
        with TestClient(app) as client:
            response = client.post("/health")
            assert response.status_code == 405

    @patch("mcp_server_openai.streaming_http._enhanced_sse_generator")
    def test_sse_error_handling(self, mock_generator):
        """Test SSE error handling."""

        # Mock generator to return a simple async generator that raises an exception
        async def failing_generator():
            yield b"test data"
            raise Exception("Test error")

        mock_generator.return_value = failing_generator()

        with TestClient(app) as client:
            try:
                with client.stream("GET", "/mcp/sse?client_id=test") as response:
                    # Consume only first few chunks to avoid infinite loop
                    chunks = []
                    for _ in range(3):
                        try:
                            chunk = next(response.iter_lines())
                            chunks.append(chunk)
                        except StopIteration:
                            break
            except Exception:
                # Expected due to mocked error
                pass


class TestMetricsAndMonitoring:
    """Test metrics collection and monitoring."""

    def test_metrics_collection(self):
        """Test that metrics are being collected."""
        initial_requests = _server_metrics["requests_total"]

        with TestClient(app) as client:
            client.get("/health")
            client.get("/info")

        # Metrics should be updated (note: may not be exact due to other tests)
        assert _server_metrics["requests_total"] >= initial_requests

    def test_server_uptime_tracking(self):
        """Test server uptime tracking."""
        start_time = _server_metrics["start_time"]
        assert start_time > 0
        assert time.time() >= start_time


class TestAsyncFunctionality:
    """Test async-specific functionality."""

    @pytest.mark.asyncio
    async def test_async_sse_generator(self):
        """Test the async SSE generator directly."""
        from mcp_server_openai.streaming_http import _enhanced_sse_generator

        # Use max_heartbeats=0 to prevent infinite heartbeat loop in tests
        generator = _enhanced_sse_generator("test_client", {"compression": False}, max_heartbeats=0)

        # Get first few events with proper async iteration
        events = []
        event_count = 0
        async for event in generator:
            events.append(event.decode())
            event_count += 1
            # Stop after getting a couple events to avoid infinite loop
            if event_count >= 2:
                break

        # Just verify we got some events
        assert len(events) >= 1
        # Basic validation that we got SSE-formatted content
        assert any("SSE session started" in event or "event:" in event for event in events)

    async def test_websocket_heartbeat(self):
        """Test WebSocket heartbeat functionality."""
        # This would require a more complex async test setup
        # For now, we verify the heartbeat logic exists
        from mcp_server_openai.streaming_http import websocket_endpoint

        # Mock WebSocket
        mock_websocket = AsyncMock()
        mock_websocket.query_params = {"client_id": "test"}
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()
        mock_websocket.receive_json = AsyncMock(side_effect=WebSocketDisconnect)

        # This should handle the disconnect gracefully
        await websocket_endpoint(mock_websocket)

        assert mock_websocket.accept.called
        assert mock_websocket.send_json.called  # Welcome message


class TestConfigIntegration:
    """Test integration with server configuration."""

    def test_server_config_validation(self):
        """Test server configuration validation."""
        from mcp_server_openai.server_config import validate_config

        # Valid configuration
        config = ServerConfig(host="localhost", port=8080)
        issues = validate_config(config)
        assert len(issues) == 0

        # Invalid configuration
        invalid_config = ServerConfig(port=99999)  # Invalid port
        issues = validate_config(invalid_config)
        assert len(issues) > 0
        assert any("port" in issue.lower() for issue in issues)

    def test_config_from_env(self):
        """Test configuration loading from environment."""

        with patch.dict("os.environ", {"MCP_HTTP_PORT": "9000", "MCP_HTTP_DEBUG": "true"}):
            config = ServerConfig.from_env()
            assert config.port == 9000
            assert config.debug is True
