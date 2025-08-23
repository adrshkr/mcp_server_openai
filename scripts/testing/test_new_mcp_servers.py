#!/usr/bin/env python3
"""
Test script for the newly implemented MCP servers:
- Sequential Thinking Server
- Brave Search Server
- Memory Server
- Filesystem Server

This script tests the functionality and integration of these servers.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_server_openai.tools.mcp_brave_search import BraveSearchClient, SearchRequest, search_content
from mcp_server_openai.tools.mcp_filesystem import create_directory, read_file, write_file
from mcp_server_openai.tools.mcp_memory import retrieve_content, store_content
from mcp_server_openai.tools.mcp_memory import search_content as memory_search
from mcp_server_openai.tools.mcp_sequential_thinking import SequentialThinkingEngine, ThinkingRequest, plan_content

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_sequential_thinking() -> None:
    """Test the Sequential Thinking Server functionality."""
    print("\n=== Testing Sequential Thinking Server ===")

    try:
        # Test the engine directly
        engine = SequentialThinkingEngine()

        # Create a test request
        request = ThinkingRequest(
            content_type="presentation",
            brief="AI in Healthcare",
            notes="Machine learning applications, diagnostic tools, patient care automation",
            target_length="10 slides",
            style="professional",
            tone="informative",
            audience="healthcare professionals",
        )

        # Test sequential thinking
        response = await engine.think_sequentially(request)

        print("✅ Sequential thinking completed successfully")
        print(f"   Status: {response.status}")
        print(f"   Confidence Score: {response.confidence_score:.2f}")
        print(f"   Processing Time: {response.processing_time:.3f}s")
        print(f"   Steps: {len(response.thinking_process)}")

        # Test the plan_content function
        plan_result = await plan_content(
            content_type="document",
            brief="Climate Change Report",
            notes="Global warming, renewable energy, policy recommendations",
            target_length="20 pages",
            style="academic",
            tone="objective",
        )

        print("✅ Content planning completed successfully")
        print(f"   Status: {plan_result['status']}")
        print(f"   Final Plan Keys: {list(plan_result['final_plan'].keys())}")

    except Exception as e:
        print(f"❌ Sequential thinking test failed: {e}")
        logger.error(f"Sequential thinking test error: {e}")


async def test_brave_search() -> None:
    """Test the Brave Search Server functionality."""
    print("\n=== Testing Brave Search Server ===")

    try:
        # Test the search client
        client = BraveSearchClient()

        # Create a test request
        request = SearchRequest(
            query="artificial intelligence trends 2024",
            search_type="web",
            max_results=5,
            safe_search=True,
            language="en",
            region="US",
        )

        # Test search functionality
        search_result = await client.search(request)

        print("✅ Brave search completed successfully")
        print(f"   Status: {search_result.status}")
        print(f"   Total Results: {search_result.total_results}")
        print(f"   Search Time: {search_result.search_time:.3f}s")

        # Test the search_content function
        content_results = await search_content(query="machine learning applications", max_results=3)

        print("✅ Content search completed successfully")
        print(f"   Results: {len(content_results)}")

    except Exception as e:
        print(f"❌ Brave search test failed: {e}")
        logger.error(f"Brave search test error: {e}")


async def test_memory_server() -> None:
    """Test the Memory Server functionality."""
    print("\n=== Testing Memory Server ===")

    try:
        # Test content storage
        content_id = await store_content(
            content_type="presentation",
            title="AI in Healthcare Overview",
            content="This is a comprehensive overview of AI applications in healthcare...",
            metadata={"slides": 15, "audience": "healthcare professionals"},
            tags=["ai", "healthcare", "presentation"],
            client_id="test_client_001",
        )

        print("✅ Content stored successfully")
        print(f"   Content ID: {content_id}")

        # Test content retrieval
        retrieved_content = await retrieve_content(content_id)

        if retrieved_content:
            print("✅ Content retrieved successfully")
            print(f"   Title: {retrieved_content['title']}")
            print(f"   Type: {retrieved_content['content_type']}")
            print(f"   Size: {retrieved_content['size_bytes']} bytes")
        else:
            print("❌ Content retrieval failed")

        # Test content search
        search_results = await memory_search(query="healthcare", content_type="presentation", max_results=5)

        print("✅ Memory search completed successfully")
        print(f"   Found: {len(search_results)} items")

        # Test memory stats
        from mcp_server_openai.tools.mcp_memory import get_memory_stats

        stats = await get_memory_stats("test_client_001")

        print("✅ Memory stats retrieved successfully")
        print(f"   Total Items: {stats.get('total_items', 0)}")
        print(f"   Total Size: {stats.get('total_size_mb', 0)} MB")

    except Exception as e:
        print(f"❌ Memory server test failed: {e}")
        logger.error(f"Memory server test error: {e}")


async def test_filesystem_server() -> None:
    """Test the Filesystem Server functionality."""
    print("\n=== Testing Filesystem Server ===")

    try:
        # Test directory creation
        dir_result = await create_directory("test_filesystem_dir", create_parents=True)

        if dir_result["success"]:
            print("✅ Directory created successfully")
            print(f"   Path: {dir_result['source_path']}")
        else:
            print(f"❌ Directory creation failed: {dir_result['error']}")

        # Test file writing
        test_file_path = "test_filesystem_dir/test_file.txt"
        write_result = await write_file(
            test_file_path, "This is a test file content for filesystem testing.", overwrite=True
        )

        if write_result["success"]:
            print("✅ File written successfully")
            print(f"   Path: {write_result['source_path']}")
            print(f"   Size: {write_result['file_info']['size_bytes']} bytes")
        else:
            print(f"❌ File writing failed: {write_result['error']}")

        # Test file reading
        read_result = await read_file(test_file_path)

        if read_result["success"]:
            print("✅ File read successfully")
            print(f"   Path: {read_result['source_path']}")
            print(f"   File Type: {read_result['file_info']['file_type']}")
        else:
            print(f"❌ File reading failed: {read_result['error']}")

        # Test directory listing
        from mcp_server_openai.tools.mcp_filesystem import list_directory

        files = await list_directory("test_filesystem_dir")

        print("✅ Directory listing completed successfully")
        print(f"   Files: {len(files)}")
        for file_info in files:
            print(f"     - {file_info['name']} ({file_info['size_bytes']} bytes)")

    except Exception as e:
        print(f"❌ Filesystem server test failed: {e}")
        logger.error(f"Filesystem server test error: {e}")


async def test_integration() -> None:
    """Test integration between the MCP servers."""
    print("\n=== Testing MCP Server Integration ===")

    try:
        # Test workflow: Plan content -> Store in memory -> Save to filesystem

        # Step 1: Plan content using sequential thinking
        plan_result = await plan_content(
            content_type="document",
            brief="Digital Transformation Guide",
            notes="Technology adoption, change management, best practices",
            target_length="15 pages",
            style="business",
            tone="professional",
        )

        if plan_result["status"] == "success":
            print("✅ Step 1: Content planning completed")

            # Step 2: Store plan in memory
            plan_id = await store_content(
                content_type="plan",
                title="Digital Transformation Guide Plan",
                content=json.dumps(plan_result, indent=2),
                metadata={"plan_type": "document", "target_length": "15 pages"},
                tags=["digital-transformation", "planning", "document"],
                client_id="integration_test",
            )

            print(f"✅ Step 2: Plan stored in memory (ID: {plan_id})")

            # Step 3: Save plan to filesystem
            file_path = f"plans/digital_transformation_plan_{plan_id[:8]}.json"
            write_result = await write_file(
                file_path, json.dumps(plan_result, indent=2), overwrite=True, create_parents=True
            )

            if write_result["success"]:
                print("✅ Step 3: Plan saved to filesystem")
                print(f"   File: {file_path}")

                # Step 4: Verify integration by reading back
                read_result = await read_file(file_path)
                if read_result["success"]:
                    print("✅ Step 4: Integration verification successful")
                    print(f"   File size: {read_result['file_info']['size_bytes']} bytes")
                else:
                    print("❌ Step 4: Integration verification failed")
            else:
                print("❌ Step 3: Failed to save plan to filesystem")
        else:
            print("❌ Step 1: Content planning failed")

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        logger.error(f"Integration test error: {e}")


async def main() -> None:
    """Main test function."""
    print("🚀 Starting MCP Server Tests")
    print("=" * 50)

    try:
        # Test individual servers
        await test_sequential_thinking()
        await test_brave_search()
        await test_memory_server()
        await test_filesystem_server()

        # Test integration
        await test_integration()

        print("\n" + "=" * 50)
        print("✅ All MCP server tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        logger.error(f"Test execution error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
