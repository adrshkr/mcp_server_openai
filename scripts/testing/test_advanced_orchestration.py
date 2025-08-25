#!/usr/bin/env python3
"""
Test script for MCP Advanced Orchestration Tool

This script tests the advanced orchestration capabilities including:
- Workflow creation and management
- Workflow execution and monitoring
- Conditional logic and decision making
- Parallel execution and loops
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_server_openai.tools.mcp_advanced_orchestration import (
    AdvancedOrchestrationEngine,
    create_workflow_definition,
    execute_workflow,
    get_execution_history,
    get_workflow_status,
    list_available_workflows,
)


async def test_orchestration_engine_creation() -> None:
    """Test creating the orchestration engine."""
    print("Testing orchestration engine creation...")

    try:
        engine = AdvancedOrchestrationEngine()
        print("✓ Advanced orchestration engine created successfully")
        print(f"  Available workflows: {len(engine.workflows)}")
        print(f"  Available tools: {len(engine.available_tools)}")

        # Check default workflows
        if "content_creation_v1" in engine.workflows:
            workflow = engine.workflows["content_creation_v1"]
            print(f"  Default workflow: {workflow.name}")
            print(f"    Steps: {len(workflow.steps)}")
            print(f"    Conditions: {len(workflow.conditions)}")
            print(f"    Entry point: {workflow.entry_point}")
            print(f"    Exit points: {workflow.exit_points}")

        return True

    except Exception as e:
        print(f"✗ Orchestration engine creation failed: {e}")
        return False


async def test_workflow_creation() -> None:
    """Test creating custom workflows."""
    print("\nTesting workflow creation...")

    try:
        # Create a simple workflow
        simple_workflow = await create_workflow_definition(
            name="Test Simple Workflow",
            description="A simple test workflow for validation",
            steps=[
                {
                    "step_id": "start",
                    "name": "Start",
                    "description": "Start the workflow",
                    "step_type": "action",
                    "tool_name": "workflow_start",
                    "parameters": {},
                    "dependencies": [],
                },
                {
                    "step_id": "process",
                    "name": "Process Data",
                    "description": "Process input data",
                    "step_type": "action",
                    "tool_name": "data_processor",
                    "parameters": {"input": "{{input_data}}"},
                    "dependencies": ["start"],
                },
                {
                    "step_id": "validate",
                    "name": "Validate Result",
                    "description": "Validate the processed result",
                    "step_type": "condition",
                    "tool_name": "validator",
                    "parameters": {"data": "{{process_result}}"},
                    "dependencies": ["process"],
                    "condition": "validation_score > 0.8",
                },
                {
                    "step_id": "finish",
                    "name": "Finish",
                    "description": "Complete the workflow",
                    "step_type": "action",
                    "tool_name": "workflow_finish",
                    "parameters": {"result": "{{validation_result}}"},
                    "dependencies": ["validate"],
                },
            ],
            conditions=[
                {
                    "condition_id": "validation_condition",
                    "name": "Validation Decision",
                    "description": "Decide based on validation result",
                    "condition_type": "if",
                    "expression": "validation_score > 0.8",
                    "true_steps": ["finish"],
                    "false_steps": ["process"],  # Retry processing
                }
            ],
            tags=["test", "simple", "validation"],
        )

        if simple_workflow["status"] == "success":
            print("✓ Simple workflow created successfully!")
            print(f"  Workflow ID: {simple_workflow['workflow_id']}")
            print(f"  Steps: {simple_workflow['steps_count']}")
            print(f"  Conditions: {simple_workflow['conditions_count']}")

            return simple_workflow["workflow_id"]
        else:
            print(f"✗ Simple workflow creation failed: {simple_workflow['message']}")
            return None

    except Exception as e:
        print(f"✗ Workflow creation test failed: {e}")
        return None


async def test_workflow_execution(workflow_id: str) -> None:
    """Test workflow execution."""
    print(f"\nTesting workflow execution for: {workflow_id}")

    try:
        # Execute workflow
        execution_result = await execute_workflow(
            workflow_id, {"input_data": "Sample data for processing", "validation_threshold": 0.8}
        )

        if execution_result["status"] == "success":
            print("✓ Workflow execution started successfully!")
            print(f"  Execution ID: {execution_result['execution_id']}")
            print(f"  Workflow ID: {execution_result['workflow_id']}")

            return execution_result["execution_id"]
        else:
            print(f"✗ Workflow execution failed: {execution_result['message']}")
            return None

    except Exception as e:
        print(f"✗ Workflow execution test failed: {e}")
        return None


def test_workflow_status(execution_id: str) -> bool:
    """Test workflow status monitoring."""
    print(f"\nTesting workflow status for: {execution_id}")

    try:
        # Get initial status
        status = get_workflow_status(execution_id)

        if status["status"] == "success":
            print("✓ Workflow status retrieved successfully!")
            print(f"  Execution Status: {status['execution_status']}")
            print(f"  Progress: {status['progress']:.1f}%")
            print(f"  Current Step: {status['current_step']}")
            print(f"  Completed Steps: {status['completed_steps']}")
            print(f"  Failed Steps: {status['failed_steps']}")
            print(f"  Skipped Steps: {status['skipped_steps']}")

            # Wait and check status again
            print("  Waiting for execution to progress...")
            time.sleep(2)

            updated_status = get_workflow_status(execution_id)
            if updated_status["status"] == "success":
                print(f"  Updated Progress: {updated_status['progress']:.1f}%")
                print(f"  Updated Status: {updated_status['execution_status']}")

            return True
        else:
            print(f"✗ Workflow status retrieval failed: {status['message']}")
            return False

    except Exception as e:
        print(f"✗ Workflow status test failed: {e}")
        return False


def test_workflow_listing() -> bool:
    """Test listing available workflows."""
    print("\nTesting workflow listing...")

    try:
        workflows = list_available_workflows()

        if workflows["status"] == "success":
            print("✓ Workflow listing successful!")
            print(f"  Total workflows: {workflows['total_count']}")

            for workflow in workflows["workflows"]:
                print(f"    - {workflow['name']} (v{workflow['version']})")
                print(f"      ID: {workflow['workflow_id']}")
                print(f"      Steps: {workflow['steps_count']}")
                print(f"      Tags: {', '.join(workflow['tags'])}")
                print()

            return True
        else:
            print(f"✗ Workflow listing failed: {workflows['message']}")
            return False

    except Exception as e:
        print(f"✗ Workflow listing test failed: {e}")
        return False


def test_execution_history() -> bool:
    """Test execution history retrieval."""
    print("\nTesting execution history...")

    try:
        history = get_execution_history(limit=10)

        if history["status"] == "success":
            print("✓ Execution history retrieved successfully!")
            print(f"  History entries: {history['total_count']}")

            if history["history"]:
                print("  Recent executions:")
                for entry in history["history"][:3]:
                    print(f"    - {entry['execution_id']}")
                    print(f"      Workflow: {entry['workflow_id']}")
                    print(f"      Status: {entry['status']}")
                    print(f"      Progress: {entry['progress']:.1f}%")
                    print(
                        f"      Duration: {entry['total_duration']:.1f}s"
                        if entry["total_duration"]
                        else "      Duration: N/A"
                    )
                    print()

            return True
        else:
            print(f"✗ Execution history retrieval failed: {history['message']}")
            return False

    except Exception as e:
        print(f"✗ Execution history test failed: {e}")
        return False


async def test_complex_workflow() -> None:
    """Test creating and executing a complex workflow."""
    print("\nTesting complex workflow...")

    try:
        # Create a complex workflow with parallel execution and loops
        complex_workflow = await create_workflow_definition(
            name="Complex Content Workflow",
            description="A complex workflow with parallel processing and conditional logic",
            steps=[
                {
                    "step_id": "start",
                    "name": "Initialize",
                    "description": "Initialize the complex workflow",
                    "step_type": "action",
                    "tool_name": "workflow_start",
                    "parameters": {},
                    "dependencies": [],
                },
                {
                    "step_id": "plan",
                    "name": "Plan Content",
                    "description": "Plan content structure",
                    "step_type": "action",
                    "tool_name": "content_planner",
                    "parameters": {"topic": "{{content_topic}}"},
                    "dependencies": ["start"],
                },
                {
                    "step_id": "research_parallel",
                    "name": "Parallel Research",
                    "description": "Conduct research in parallel",
                    "step_type": "parallel",
                    "tool_name": "parallel_researcher",
                    "parameters": {"topics": "{{research_topics}}"},
                    "dependencies": ["plan"],
                    "parallel_group": "research",
                },
                {
                    "step_id": "generate",
                    "name": "Generate Content",
                    "description": "Generate content based on research",
                    "step_type": "action",
                    "tool_name": "content_generator",
                    "parameters": {"research": "{{research_results}}"},
                    "dependencies": ["research_parallel"],
                },
                {
                    "step_id": "validate",
                    "name": "Validate Content",
                    "description": "Validate generated content",
                    "step_type": "condition",
                    "tool_name": "content_validator",
                    "parameters": {"content": "{{generated_content}}"},
                    "dependencies": ["generate"],
                    "condition": "validation_score >= 0.9",
                },
                {
                    "step_id": "enhance",
                    "name": "Enhance Content",
                    "description": "Enhance content if validation fails",
                    "step_type": "loop",
                    "tool_name": "content_enhancer",
                    "parameters": {"content": "{{generated_content}}"},
                    "dependencies": ["validate"],
                    "loop_config": {"max_iterations": 3, "condition": "validation_score < 0.9"},
                },
                {
                    "step_id": "finish",
                    "name": "Complete",
                    "description": "Complete the workflow",
                    "step_type": "action",
                    "tool_name": "workflow_finish",
                    "parameters": {"final_content": "{{enhanced_content}}"},
                    "dependencies": ["enhance", "validate"],
                },
            ],
            conditions=[
                {
                    "condition_id": "validation_decision",
                    "name": "Validation Decision",
                    "description": "Decide whether to enhance content",
                    "condition_type": "if",
                    "expression": "validation_score >= 0.9",
                    "true_steps": ["finish"],
                    "false_steps": ["enhance"],
                }
            ],
            tags=["complex", "parallel", "conditional", "loop"],
        )

        if complex_workflow["status"] == "success":
            print("✓ Complex workflow created successfully!")
            print(f"  Workflow ID: {complex_workflow['workflow_id']}")
            print(f"  Steps: {complex_workflow['steps_count']}")
            print(f"  Conditions: {complex_workflow['conditions_count']}")

            # Execute complex workflow
            execution_result = await execute_workflow(
                complex_workflow["workflow_id"],
                {
                    "content_topic": "AI in Healthcare",
                    "research_topics": ["AI applications", "Healthcare trends", "Implementation challenges"],
                    "validation_threshold": 0.9,
                },
            )

            if execution_result["status"] == "success":
                print("✓ Complex workflow execution started!")
                print(f"  Execution ID: {execution_result['execution_id']}")

                # Monitor execution
                time.sleep(1)
                status = get_workflow_status(execution_result["execution_id"])
                if status["status"] == "success":
                    print(f"  Initial Status: {status['execution_status']}")
                    print(f"  Progress: {status['progress']:.1f}%")

                return complex_workflow["workflow_id"]
            else:
                print(f"✗ Complex workflow execution failed: {execution_result['message']}")
                return None
        else:
            print(f"✗ Complex workflow creation failed: {complex_workflow['message']}")
            return None

    except Exception as e:
        print(f"✗ Complex workflow test failed: {e}")
        return None


async def test_integration() -> bool:
    """Test integration between orchestration components."""
    print("\nTesting orchestration integration...")

    try:
        # Test workflow: Create -> Execute -> Monitor -> History
        print("  Running integration workflow...")

        # Step 1: Create workflow
        workflow = await create_workflow_definition(
            name="Integration Test Workflow",
            description="Workflow for testing integration",
            steps=[
                {
                    "step_id": "start",
                    "name": "Start",
                    "description": "Start integration test",
                    "step_type": "action",
                    "tool_name": "test_start",
                    "parameters": {},
                    "dependencies": [],
                },
                {
                    "step_id": "test",
                    "name": "Run Test",
                    "description": "Run integration test",
                    "step_type": "action",
                    "tool_name": "integration_tester",
                    "parameters": {"test_data": "{{test_input}}"},
                    "dependencies": ["start"],
                },
                {
                    "step_id": "finish",
                    "name": "Finish",
                    "description": "Complete integration test",
                    "step_type": "action",
                    "tool_name": "test_finish",
                    "parameters": {"result": "{{test_result}}"},
                    "dependencies": ["test"],
                },
            ],
            tags=["integration", "test"],
        )

        if workflow["status"] != "success":
            print("    ✗ Workflow creation failed")
            return False

        print("    ✓ Workflow created")

        # Step 2: Execute workflow
        execution = await execute_workflow(workflow["workflow_id"], {"test_input": "Integration test data"})

        if execution["status"] != "success":
            print("    ✗ Workflow execution failed")
            return False

        print("    ✓ Workflow executed")

        # Step 3: Monitor execution
        time.sleep(1)
        status = get_workflow_status(execution["execution_id"])
        if status["status"] != "success":
            print("    ✗ Status monitoring failed")
            return False

        print("    ✓ Status monitored")

        # Step 4: Check history
        history = get_execution_history(limit=5)
        if history["status"] != "success":
            print("    ✗ History retrieval failed")
            return False

        # Check if our execution is in history
        execution_found = any(entry["execution_id"] == execution["execution_id"] for entry in history["history"])

        if execution_found:
            print("    ✓ History integration verified")
            print("    ✓ Integration workflow completed successfully!")
            return True
        else:
            print("    ✗ Execution not found in history")
            return False

    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False


async def main() -> None:
    """Run all tests."""
    print("MCP Advanced Orchestration Tool - Test Suite")
    print("=" * 50)

    test_results = []

    # Test 1: Engine creation
    test_results.append(await test_orchestration_engine_creation())

    # Test 2: Workflow creation
    workflow_id = await test_workflow_creation()
    test_results.append(workflow_id is not None)

    # Test 3: Workflow execution
    if workflow_id:
        execution_id = await test_workflow_execution(workflow_id)
        test_results.append(execution_id is not None)

        # Test 4: Status monitoring
        if execution_id:
            test_results.append(test_workflow_status(execution_id))
        else:
            test_results.append(False)
    else:
        test_results.extend([False, False])

    # Test 5: Workflow listing
    test_results.append(test_workflow_listing())

    # Test 6: Execution history
    test_results.append(test_execution_history())

    # Test 7: Complex workflow
    complex_workflow_id = await test_complex_workflow()
    test_results.append(complex_workflow_id is not None)

    # Test 8: Integration
    test_results.append(await test_integration())

    # Summary
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    passed = sum(test_results)
    total = len(test_results)

    for i, result in enumerate(test_results, 1):
        status = "PASSED" if result else "FAILED"
        print(f"  Test {i}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The advanced orchestration tool is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
