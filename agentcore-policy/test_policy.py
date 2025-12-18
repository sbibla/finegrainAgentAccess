
"""
Test Policy Engine with direct HTTP calls to Gateway
Run after setup: python test_policy.py
"""

import json
import sys
import requests
from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient


def test_refund(gateway_url, bearer_token, amount):
    """Test a refund request - print raw response"""
    response = requests.post(
        gateway_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}",
        },
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "RefundTarget___process_refund",
                "arguments": {"amount": amount}
            },
        },
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    return response


def main():
    print("=" * 60)
    print("🧪 Testing Policy Engine")
    print("=" * 60 + "\n")
    
    # Load configuration
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Error: config.json not found!")
        print("Please run 'python setup_policy.py' first.")
        sys.exit(1)
    
    gateway_url = config["gateway_url"]
    refund_limit = config["refund_limit"]
    
    print(f"Gateway: {gateway_url}")
    print(f"Refund limit: ${refund_limit}\n")
    
    # Get access token
    print("🔑 Getting access token...")
    gateway_client = GatewayClient(region_name=config["region"])
    token = gateway_client.get_access_token_for_cognito(config["client_info"])
    print("✅ Token obtained\n")
    
    # Test 1: Refund $500 (should be allowed)
    print(f"📝 Test 1: Refund $500 (Expected: ALLOW)")
    print("-" * 40)
    test_refund(gateway_url, token, 500)
    print()
    
    # Test 2: Refund $2000 (should be denied)  
    print(f"📝 Test 2: Refund $1500 (Expected: DENY)")
    print("-" * 40)
    test_refund(gateway_url, token, 1500)
    print()
    
    print("=" * 60)
    print("✅ Testing complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
  