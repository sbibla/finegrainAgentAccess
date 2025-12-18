
"""
Cleanup script to remove Gateway and Policy Engine resources
Run this to clean up: python cleanup_policy.py
"""

from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
from bedrock_agentcore_starter_toolkit.operations.policy.client import PolicyClient
import json


def cleanup():
    with open("config.json", "r") as f:
        config = json.load(f)
    
    # Clean up Policy Engine first
    print("🧹 Cleaning up Policy Engine...")
    policy_client = PolicyClient(region_name=config["region"])
    policy_client.cleanup_policy_engine(config["policy_engine_id"])
    print("✓ Policy Engine cleaned up\n")
    
    # Then clean up Gateway
    print("🧹 Cleaning up Gateway...")
    gateway_client = GatewayClient(region_name=config["region"])
    gateway_client.cleanup_gateway(config["gateway_id"], config["client_info"])
    print("✅ Cleanup complete!")


if __name__ == "__main__":
    cleanup()
  