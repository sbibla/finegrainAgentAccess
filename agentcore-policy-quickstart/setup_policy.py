
"""
Setup script to create Gateway with Policy Engine
Run this first: python setup_policy.py
"""

from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
from bedrock_agentcore_starter_toolkit.operations.policy.client import PolicyClient
from bedrock_agentcore_starter_toolkit.utils.lambda_utils import create_lambda_function
import boto3
import json
import logging
import time


def setup_policy():
    # Configuration
    region = "us-west-2"
    refund_limit = 1000
    
    print("🚀 Setting up AgentCore Gateway with Policy Engine...")
    print(f"Region: {region}\n")
    
    # Initialize clients
    gateway_client = GatewayClient(region_name=region)
    gateway_client.logger.setLevel(logging.INFO)
    
    policy_client = PolicyClient(region_name=region)
    policy_client.logger.setLevel(logging.INFO)
    
    # Step 1: Create OAuth authorizer
    print("Step 1: Creating OAuth authorization server...")
    cognito_response = gateway_client.create_oauth_authorizer_with_cognito("PolicyGateway")
    print("✓ Authorization server created\n")
    
    # Step 2: Create Gateway
    print("Step 2: Creating Gateway...")
    gateway = gateway_client.create_mcp_gateway(
        name=None,
        role_arn=None,
        authorizer_config=cognito_response["authorizer_config"],
        enable_semantic_search=False,
    )
    print(f"✓ Gateway created: {gateway['gatewayUrl']}\n")
    
    # Fix IAM permissions
    gateway_client.fix_iam_permissions(gateway)
    print("⏳ Waiting 30s for IAM propagation...")
    time.sleep(30)
    print("✓ IAM permissions configured\n")
    
    # Step 3: Create Lambda function with refund tool
    print("Step 3: Creating Lambda function with refund tool...")
    
    refund_lambda_code = """
def lambda_handler(event, context):
    amount = event.get('amount', 0)
    return {
        "status": "success",
        "message": f"Refund of ${amount} processed successfully",
        "amount": amount
    }
"""
    
    session = boto3.Session(region_name=region)
    lambda_arn = create_lambda_function(
        session=session,
        logger=gateway_client.logger,
        function_name=f"RefundTool-{int(time.time())}",
        lambda_code=refund_lambda_code,
        runtime="python3.13",
        handler="lambda_function.lambda_handler",
        gateway_role_arn=gateway["roleArn"],
        description="Refund tool for policy demo",
    )
    print("✓ Lambda function created\n")
    
    # Step 4: Add Lambda target with refund tool schema
    print("Step 4: Adding Lambda target with refund tool schema...")
    lambda_target = gateway_client.create_mcp_gateway_target(
        gateway=gateway,
        name="RefundTarget",
        target_type="lambda",
        target_payload={
            "lambdaArn": lambda_arn,
            "toolSchema": {
                "inlinePayload": [
                    {
                        "name": "process_refund",
                        "description": "Process a customer refund",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "amount": {
                                    "type": "integer",
                                    "description": "Refund amount in dollars"
                                }
                            },
                            "required": ["amount"],
                        },
                    }
                ]
            },
        },
        credentials=None,
    )
    print("✓ Lambda target added\n")
    
    # Step 5: Create Policy Engine
    print("Step 5: Creating Policy Engine...")
    engine = policy_client.create_or_get_policy_engine(
        name="RefundPolicyEngine",
        description="Policy engine for refund governance"
    )
    print(f"✓ Policy Engine: {engine['policyEngineId']}\n")
    
    # Step 6: Create Cedar policy
    print(f"Step 6: Creating Cedar policy (refund limit: ${refund_limit})...")
    cedar_statement = (
        f"permit(principal, "
        f'action == AgentCore::Action::"RefundTarget___process_refund", '
        f'resource == AgentCore::Gateway::"{gateway["gatewayArn"]}") '
        f"when {{ context.input.amount < {refund_limit} }};"
    )
    
    policy = policy_client.create_or_get_policy(
        policy_engine_id=engine["policyEngineId"],
        name="refund_limit_policy",
        description=f"Allow refunds under ${refund_limit}",
        definition={"cedar": {"statement": cedar_statement}},
    )
    print(f"✓ Policy: {policy['policyId']}\n")
    
    # Step 7: Attach Policy Engine to Gateway
    print("Step 7: Attaching Policy Engine to Gateway (ENFORCE mode)...")
    gateway_client.update_gateway_policy_engine(
        gateway_identifier=gateway["gatewayId"],
        policy_engine_arn=engine["policyEngineArn"],
        mode="ENFORCE"
    )
    print("✓ Policy Engine attached to Gateway\n")
    
    # Step 8: Save configuration
    config = {
        "gateway_url": gateway["gatewayUrl"],
        "gateway_id": gateway["gatewayId"],
        "gateway_arn": gateway["gatewayArn"],
        "policy_engine_id": engine["policyEngineId"],
        "policy_engine_arn": engine["policyEngineArn"],
        "policy_id": policy["policyId"],
        "region": region,
        "client_info": cognito_response["client_info"],
        "refund_limit": refund_limit
    }
    
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("=" * 60)
    print("✅ Setup complete!")
    print(f"Gateway URL: {gateway['gatewayUrl']}")
    print(f"Policy Engine ID: {engine['policyEngineId']}")
    print(f"Refund limit: ${refund_limit}")
    print("\nConfiguration saved to: config.json")
    print("\nNext step: Run 'python test_policy.py' to test your Policy")
    print("=" * 60)
    
    return config


if __name__ == "__main__":
    setup_policy()
  