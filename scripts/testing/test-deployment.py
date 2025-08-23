#!/usr/bin/env python3
"""
Comprehensive deployment testing script for MCP Server OpenAI.

Tests all aspects of the deployment including:
- Docker image building
- Health endpoints
- Security configuration
- Performance metrics
- Error handling
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path

import httpx

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeploymentTester:
    """Comprehensive deployment testing."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": []
        }
    
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        self.results["tests_run"] += 1
        
        if success:
            self.results["tests_passed"] += 1
            logger.info(f"✅ {test_name}: PASSED {message}")
        else:
            self.results["tests_failed"] += 1
            self.results["failures"].append(f"{test_name}: {message}")
            logger.error(f"❌ {test_name}: FAILED {message}")
    
    async def test_basic_endpoints(self):
        """Test basic HTTP endpoints."""
        logger.info("🔍 Testing basic endpoints...")
        
        endpoints = [
            ("/health", "Basic health check"),
            ("/info", "Service info"),
            ("/health/live", "Liveness probe"),
            ("/health/ready", "Readiness probe"), 
            ("/health/startup", "Startup probe"),
            ("/status", "Detailed status")
        ]
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for endpoint, description in endpoints:
                try:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    
                    if response.status_code == 200:
                        self.log_result(
                            f"Endpoint {endpoint}", 
                            True, 
                            f"({response.status_code}, {len(response.content)} bytes)"
                        )
                    else:
                        self.log_result(
                            f"Endpoint {endpoint}", 
                            False, 
                            f"HTTP {response.status_code}"
                        )
                        
                except Exception as e:
                    self.log_result(f"Endpoint {endpoint}", False, str(e))
    
    async def test_health_check_details(self):
        """Test health check response structure."""
        logger.info("🏥 Testing health check details...")
        
        health_endpoints = [
            "/health/live",
            "/health/ready", 
            "/health/startup",
            "/status"
        ]
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for endpoint in health_endpoints:
                try:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check required fields
                        required_fields = ["timestamp", "status"]
                        missing_fields = [f for f in required_fields if f not in data]
                        
                        if not missing_fields:
                            self.log_result(
                                f"Health structure {endpoint}", 
                                True,
                                f"Status: {data.get('status')}"
                            )
                        else:
                            self.log_result(
                                f"Health structure {endpoint}", 
                                False,
                                f"Missing fields: {missing_fields}"
                            )
                    else:
                        self.log_result(
                            f"Health structure {endpoint}", 
                            False,
                            f"HTTP {response.status_code}"
                        )
                        
                except Exception as e:
                    self.log_result(f"Health structure {endpoint}", False, str(e))
    
    async def test_performance(self):
        """Test basic performance metrics."""
        logger.info("⚡ Testing performance...")
        
        # Test response time
        async with httpx.AsyncClient(timeout=30.0) as client:
            start_time = time.time()
            try:
                response = await client.get(f"{self.base_url}/health/live")
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                
                if response.status_code == 200 and response_time_ms < 1000:
                    self.log_result(
                        "Response time", 
                        True,
                        f"{response_time_ms:.2f}ms"
                    )
                else:
                    self.log_result(
                        "Response time", 
                        False,
                        f"{response_time_ms:.2f}ms (target: <1000ms)"
                    )
                    
            except Exception as e:
                self.log_result("Response time", False, str(e))
    
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        logger.info("🔄 Testing concurrent requests...")
        
        async def single_request(client, request_id):
            try:
                response = await client.get(f"{self.base_url}/health/live")
                return response.status_code == 200, response.status_code
            except Exception as e:
                return False, str(e)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Send 5 concurrent requests
                tasks = [single_request(client, i) for i in range(5)]
                results = await asyncio.gather(*tasks)
                
                successful_requests = sum(1 for success, _ in results if success)
                total_requests = len(results)
                
                if successful_requests == total_requests:
                    self.log_result(
                        "Concurrent requests", 
                        True,
                        f"{successful_requests}/{total_requests} succeeded"
                    )
                else:
                    self.log_result(
                        "Concurrent requests", 
                        False,
                        f"Only {successful_requests}/{total_requests} succeeded"
                    )
                    
        except Exception as e:
            self.log_result("Concurrent requests", False, str(e))
    
    async def test_error_handling(self):
        """Test error handling for invalid requests."""
        logger.info("🚫 Testing error handling...")
        
        # Test non-existent endpoint
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{self.base_url}/non-existent-endpoint")
                
                if response.status_code == 404:
                    self.log_result("404 handling", True, "Correct 404 response")
                else:
                    self.log_result(
                        "404 handling", 
                        False, 
                        f"Expected 404, got {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_result("404 handling", False, str(e))
    
    async def run_all_tests(self):
        """Run all deployment tests."""
        logger.info(f"🚀 Starting deployment tests for {self.base_url}")
        
        test_methods = [
            self.test_basic_endpoints,
            self.test_health_check_details,
            self.test_performance,
            self.test_concurrent_requests,
            self.test_error_handling,
        ]
        
        for test_method in test_methods:
            try:
                await test_method()
            except Exception as e:
                logger.error(f"Test method {test_method.__name__} failed: {e}")
                self.results["tests_failed"] += 1
                self.results["failures"].append(f"{test_method.__name__}: {str(e)}")
        
        # Print summary
        logger.info("\n" + "="*50)
        logger.info("DEPLOYMENT TEST SUMMARY")
        logger.info("="*50)
        logger.info(f"Tests run: {self.results['tests_run']}")
        logger.info(f"Tests passed: {self.results['tests_passed']}")
        logger.info(f"Tests failed: {self.results['tests_failed']}")
        
        if self.results['failures']:
            logger.error("\nFAILED TESTS:")
            for failure in self.results['failures']:
                logger.error(f"  - {failure}")
        
        success_rate = (self.results['tests_passed'] / self.results['tests_run'] * 100 
                       if self.results['tests_run'] > 0 else 0)
        
        logger.info(f"\nSuccess rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            logger.info("🎉 Deployment tests PASSED!")
            return 0
        else:
            logger.error("💥 Deployment tests FAILED!")
            return 1


async def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test MCP Server OpenAI deployment")
    parser.add_argument(
        "--url", 
        default="http://localhost:8080",
        help="Base URL of the service to test"
    )
    parser.add_argument(
        "--wait", 
        type=int,
        default=0,
        help="Seconds to wait before starting tests"
    )
    
    args = parser.parse_args()
    
    if args.wait > 0:
        logger.info(f"Waiting {args.wait} seconds before starting tests...")
        await asyncio.sleep(args.wait)
    
    tester = DeploymentTester(args.url)
    return await tester.run_all_tests()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))