#!/usr/bin/env python3
"""
Comprehensive endpoint testing script for all enhanced tools.

This script tests all individual REST API endpoints for:
- Enhanced PPT Generator
- Enhanced Document Generator  
- Enhanced Image Generator
- Enhanced Icon Generator
- Enhanced Content Creator
- Unified Content Creator
- System endpoints
"""

import asyncio
import json
import time
from typing import Dict, Any, List
import httpx
from pathlib import Path


class EndpointTester:
    """Comprehensive endpoint tester for all enhanced tools."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results: Dict[str, Dict[str, Any]] = {}
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def test_endpoint(self, method: str, endpoint: str, data: Dict[str, Any] = None, 
                           expected_status: int = 200) -> Dict[str, Any]:
        """Test a single endpoint and return results."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = await self.client.get(url)
            elif method.upper() == "POST":
                response = await self.client.post(url, json=data or {})
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            success = response.status_code == expected_status
            
            result = {
                "success": success,
                "status_code": response.status_code,
                "response_time": round(response_time, 3),
                "response_size": len(response.content),
                "error": None
            }
            
            if success:
                try:
                    result["response_data"] = response.json()
                except:
                    result["response_data"] = response.text[:200] + "..." if len(response.text) > 200 else response.text
            else:
                result["error"] = f"Expected {expected_status}, got {response.status_code}"
                try:
                    result["error_details"] = response.json()
                except:
                    result["error_details"] = response.text[:200] + "..." if len(response.text) > 200 else response.text
                    
        except Exception as e:
            response_time = time.time() - start_time
            result = {
                "success": False,
                "status_code": None,
                "response_time": round(response_time, 3),
                "response_size": 0,
                "error": str(e),
                "error_details": None
            }
        
        return result
    
    async def test_enhanced_ppt_endpoints(self) -> Dict[str, Any]:
        """Test all Enhanced PPT Generator endpoints."""
        print("🔍 Testing Enhanced PPT Generator endpoints...")
        
        results = {}
        
        # Test templates endpoint
        results["templates"] = await self.test_endpoint("GET", "/api/v1/ppt/templates")
        
        # Test analyze endpoint
        analyze_data = {
            "content": "Sample presentation content for analysis",
            "target_audience": "executives",
            "style": "professional"
        }
        results["analyze"] = await self.test_endpoint("POST", "/api/v1/ppt/analyze", analyze_data)
        
        # Test generate endpoint (this might take longer)
        generate_data = {
            "notes": ["Introduction to AI", "Machine Learning Basics", "Future Applications"],
            "brief": "AI Fundamentals Presentation",
            "target_length": "3 slides",
            "template_preference": "professional",
            "include_images": True,
            "language": "en",
            "client_id": "test_client"
        }
        results["generate"] = await self.test_endpoint("POST", "/api/v1/ppt/generate", generate_data)
        
        # Test status endpoint (using a dummy job_id)
        results["status"] = await self.test_endpoint("GET", "/api/v1/ppt/status/test_job_123")
        
        return results
    
    async def test_enhanced_document_endpoints(self) -> Dict[str, Any]:
        """Test all Enhanced Document Generator endpoints."""
        print("📄 Testing Enhanced Document Generator endpoints...")
        
        results = {}
        
        # Test templates endpoint
        results["templates"] = await self.test_endpoint("GET", "/api/v1/document/templates")
        
        # Test formats endpoint
        results["formats"] = await self.test_endpoint("GET", "/api/v1/document/formats")
        
        # Test generate endpoint
        generate_data = {
            "content": "# Sample Document\n\nThis is a test document with markdown content.",
            "output_format": "html",
            "template": "professional",
            "language": "en",
            "include_images": False,
            "include_icons": False,
            "custom_css": "",
            "metadata": {"title": "Test Document", "author": "Test User"}
        }
        results["generate"] = await self.test_endpoint("POST", "/api/v1/document/generate", generate_data)
        
        # Test status endpoint
        results["status"] = await self.test_endpoint("GET", "/api/v1/document/status/test_doc_123")
        
        return results
    
    async def test_enhanced_image_endpoints(self) -> Dict[str, Any]:
        """Test all Enhanced Image Generator endpoints."""
        print("🖼️ Testing Enhanced Image Generator endpoints...")
        
        results = {}
        
        # Test providers endpoint
        results["providers"] = await self.test_endpoint("GET", "/api/v1/image/providers")
        
        # Test generate endpoint
        generate_data = {
            "prompt": "A beautiful sunset over mountains",
            "provider": "unsplash",
            "style": "realistic",
            "size": "1024x1024",
            "count": 1,
            "language": "en"
        }
        results["generate"] = await self.test_endpoint("POST", "/api/v1/image/generate", generate_data)
        
        # Test status endpoint
        results["status"] = await self.test_endpoint("GET", "/api/v1/image/status/test_img_123")
        
        return results
    
    async def test_enhanced_icon_endpoints(self) -> Dict[str, Any]:
        """Test all Enhanced Icon Generator endpoints."""
        print("🎨 Testing Enhanced Icon Generator endpoints...")
        
        results = {}
        
        # Test providers endpoint
        results["providers"] = await self.test_endpoint("GET", "/api/v1/icon/providers")
        
        # Test search endpoint
        results["search"] = await self.test_endpoint("GET", "/api/v1/icon/search?q=home&provider=iconify&style=outline")
        
        # Test generate endpoint
        generate_data = {
            "query": "home icon",
            "provider": "iconify",
            "style": "outline",
            "size": "24",
            "color": "#000000",
            "count": 1,
            "language": "en"
        }
        results["generate"] = await self.test_endpoint("POST", "/api/v1/icon/generate", generate_data)
        
        # Test status endpoint
        results["status"] = await self.test_endpoint("GET", "/api/v1/icon/status/test_icon_123")
        
        return results
    
    async def test_enhanced_content_endpoints(self) -> Dict[str, Any]:
        """Test all Enhanced Content Creator endpoints."""
        print("📝 Testing Enhanced Content Creator endpoints...")
        
        results = {}
        
        # Test templates endpoint
        results["templates"] = await self.test_endpoint("GET", "/api/v1/content/templates")
        
        # Test create endpoint
        create_data = {
            "title": "Test Content",
            "content_type": "presentation",
            "brief": "A test presentation about content creation",
            "notes": ["Introduction", "Main points", "Conclusion"],
            "target_length": "short",
            "content_style": "professional",
            "include_images": False,
            "include_icons": False,
            "language": "en"
        }
        results["create"] = await self.test_endpoint("POST", "/api/v1/content/create", create_data)
        
        # Test status endpoint
        results["status"] = await self.test_endpoint("GET", "/api/v1/content/status/test_content_123")
        
        return results
    
    async def test_unified_content_endpoints(self) -> Dict[str, Any]:
        """Test all Unified Content Creator endpoints."""
        print("🔄 Testing Unified Content Creator endpoints...")
        
        results = {}
        
        # Test formats endpoint
        results["formats"] = await self.test_endpoint("GET", "/api/v1/unified/formats")
        
        # Test create endpoint
        create_data = {
            "brief": "Comprehensive test of unified content creation",
            "notes": ["Test section 1", "Test section 2", "Test section 3"],
            "output_formats": ["presentation", "document"],
            "content_style": "professional",
            "include_images": False,
            "include_icons": False,
            "language": "en",
            "client_id": "test_unified_client"
        }
        results["create"] = await self.test_endpoint("POST", "/api/v1/unified/create", create_data)
        
        # Test status endpoint
        results["status"] = await self.test_endpoint("GET", "/api/v1/unified/status/test_unified_client")
        
        return results
    
    async def test_system_endpoints(self) -> Dict[str, Any]:
        """Test all system endpoints."""
        print("⚙️ Testing System endpoints...")
        
        results = {}
        
        # Test health endpoint
        results["health"] = await self.test_endpoint("GET", "/health")
        
        # Test info endpoint
        results["info"] = await self.test_endpoint("GET", "/info")
        
        # Test metrics endpoint
        results["metrics"] = await self.test_endpoint("GET", "/metrics")
        
        # Test usage endpoint
        results["usage"] = await self.test_endpoint("GET", "/usage")
        
        # Test SSE endpoint
        results["sse"] = await self.test_endpoint("GET", "/mcp/sse")
        
        # Test stream endpoint
        results["stream"] = await self.test_endpoint("GET", "/stream")
        
        return results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all endpoint tests and return comprehensive results."""
        print("🚀 Starting comprehensive endpoint testing...")
        print(f"📍 Base URL: {self.base_url}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test all endpoint categories
        self.test_results["enhanced_ppt"] = await self.test_enhanced_ppt_endpoints()
        self.test_results["enhanced_document"] = await self.test_enhanced_document_endpoints()
        self.test_results["enhanced_image"] = await self.test_enhanced_image_endpoints()
        self.test_results["enhanced_icon"] = await self.test_enhanced_icon_endpoints()
        self.test_results["enhanced_content"] = await self.test_enhanced_content_endpoints()
        self.test_results["unified_content"] = await self.test_enhanced_content_endpoints()
        self.test_results["system"] = await self.test_system_endpoints()
        
        total_time = time.time() - start_time
        
        # Calculate summary statistics
        summary = self._calculate_summary()
        summary["total_test_time"] = round(total_time, 3)
        
        self.test_results["summary"] = summary
        
        return self.test_results
    
    def _calculate_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics from test results."""
        total_tests = 0
        successful_tests = 0
        failed_tests = 0
        total_response_time = 0.0
        total_response_size = 0
        
        for category, tests in self.test_results.items():
            if category == "summary":
                continue
                
            for test_name, result in tests.items():
                total_tests += 1
                if result["success"]:
                    successful_tests += 1
                else:
                    failed_tests += 1
                
                if result["response_time"]:
                    total_response_time += result["response_time"]
                if result["response_size"]:
                    total_response_size += result["response_size"]
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": round((successful_tests / total_tests * 100), 2) if total_tests > 0 else 0,
            "average_response_time": round(total_response_time / total_tests, 3) if total_tests > 0 else 0,
            "total_response_size": total_response_size
        }
    
    def print_results(self):
        """Print formatted test results."""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE ENDPOINT TEST RESULTS")
        print("=" * 60)
        
        # Print summary first
        if "summary" in self.test_results:
            summary = self.test_results["summary"]
            print(f"\n🎯 OVERALL SUMMARY:")
            print(f"   Total Tests: {summary['total_tests']}")
            print(f"   Successful: {summary['successful_tests']} ✅")
            print(f"   Failed: {summary['failed_tests']} ❌")
            print(f"   Success Rate: {summary['success_rate']}%")
            print(f"   Average Response Time: {summary['average_response_time']}s")
            print(f"   Total Test Time: {summary['total_test_time']}s")
        
        # Print detailed results by category
        for category, tests in self.test_results.items():
            if category == "summary":
                continue
                
            print(f"\n🔧 {category.upper().replace('_', ' ')}:")
            
            for test_name, result in tests.items():
                status_icon = "✅" if result["success"] else "❌"
                response_time = f"{result['response_time']}s" if result["response_time"] else "N/A"
                
                print(f"   {status_icon} {test_name}: {response_time}")
                
                if not result["success"] and result["error"]:
                    print(f"      Error: {result['error']}")
        
        print("\n" + "=" * 60)
    
    def save_results(self, filename: str = "endpoint_test_results.json"):
        """Save test results to a JSON file."""
        output_path = Path("output") / filename
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"💾 Test results saved to: {output_path}")


async def main():
    """Main function to run all endpoint tests."""
    # Check if server is running
    print("🔍 Checking if server is running...")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://127.0.0.1:8000/health")
            if response.status_code == 200:
                print("✅ Server is running and responding")
            else:
                print(f"⚠️ Server responded with status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print(
            "💡 Make sure the server is running with: "
            "uv run uvicorn mcp_server_openai.streaming_http:app --host 0.0.0.0 --port 8000"
        )
        return
    
    # Run all tests
    async with EndpointTester() as tester:
        results = await tester.run_all_tests()
        tester.print_results()
        tester.save_results()


if __name__ == "__main__":
    asyncio.run(main())


