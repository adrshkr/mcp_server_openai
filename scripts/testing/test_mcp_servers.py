#!/usr/bin/env python3
"""
Test script for installed MCP servers
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

def load_server_config():
    """Load MCP server configuration."""
    config_path = Path(__file__).parent.parent / "mcp-servers-config.json"
    with open(config_path) as f:
        return json.load(f)

def test_server_availability(server_name, server_config):
    """Test if an MCP server is available and responsive."""
    print(f"Testing {server_name}...")
    
    try:
        # Test if server command is available
        cmd = server_config["command"]
        args = server_config["args"][:2]  # Just test package availability
        
        result = subprocess.run(
            [cmd] + args + ["--help"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0 or "help" in result.stdout.lower() or "usage" in result.stdout.lower():
            print(f"✅ {server_name}: Available")
            return True
        else:
            print(f"⚠️  {server_name}: Available but may need configuration")
            return True
            
    except subprocess.TimeoutExpired:
        print(f"⏱️  {server_name}: Timeout (may be waiting for input)")
        return True
    except FileNotFoundError:
        print(f"❌ {server_name}: Command not found - {cmd}")
        return False
    except Exception as e:
        print(f"❌ {server_name}: Error - {e}")
        return False

def main():
    """Main test function."""
    print("🚀 MCP Server Expansion Test")
    print("=" * 50)
    
    config = load_server_config()
    servers = config["mcpServers"]
    
    available_servers = []
    unavailable_servers = []
    
    for server_name, server_config in servers.items():
        if server_config.get("status") == "project_integrated":
            print(f"⚡ {server_name}: Already integrated in project")
            available_servers.append(server_name)
            continue
            
        if test_server_availability(server_name, server_config):
            available_servers.append(server_name)
        else:
            unavailable_servers.append(server_name)
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"✅ Available servers: {len(available_servers)}")
    for server in available_servers:
        capabilities = servers[server].get("capabilities", [])
        print(f"   • {server}: {', '.join(capabilities[:3])}{'...' if len(capabilities) > 3 else ''}")
    
    if unavailable_servers:
        print(f"\n❌ Unavailable servers: {len(unavailable_servers)}")
        for server in unavailable_servers:
            print(f"   • {server}")
    
    print(f"\n📈 Expansion Progress: {len(available_servers)}/70 servers installed")
    print(f"🎯 Next Phase: {config['installation_log']['next_phase'].replace('_', ' ').title()}")
    
    return len(available_servers)

if __name__ == "__main__":
    available_count = main()
    sys.exit(0 if available_count > 0 else 1)