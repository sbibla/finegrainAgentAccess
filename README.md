# Fine-Grained Agent Access Control

This repository demonstrates testing and implementing **AgentCore Policy Engine** for fine-grained access control to AI agents and their tools. It showcases how to use Cedar policies to govern agent actions and enforce business rules at the gateway level.

## 🎯 Purpose

This project tests AgentCore's policy capabilities by creating a practical example: a refund processing system with policy-based limits. It demonstrates how to:

- Control which actions agents can perform
- Enforce business rules (e.g., refund amount limits)
- Use Cedar policies for declarative access control
- Test policy enforcement in real-time

## 📁 Project Structure

```
agentcore-policy-quickstart/
├── setup_policy.py     # Main setup script
├── test_policy.py      # Policy testing script
├── cleanup_policy.py   # Resource cleanup script
└── config.json         # Generated configuration (after setup)
```

## 🚀 What Does `setup_policy.py` Do?

The `setup_policy.py` script is the main setup script that creates and configures the entire policy-based agent access control infrastructure. Here's what it does step-by-step:

### Step 1: Create OAuth Authorization Server
Creates an OAuth authorizer using AWS Cognito for secure authentication to the gateway.

### Step 2: Create AgentCore Gateway
Sets up an MCP (Model Context Protocol) gateway that acts as the entry point for all agent requests.

### Step 3: Configure IAM Permissions
Fixes and configures the necessary IAM permissions for the gateway to function properly, with a 30-second wait for IAM propagation.

### Step 4: Create Lambda Function with Refund Tool
Deploys an AWS Lambda function that processes refund requests. This serves as the backend tool that agents can invoke through the gateway.

### Step 5: Register Lambda Target
Registers the Lambda function as an MCP target with a defined tool schema (`process_refund`) that accepts an `amount` parameter.

### Step 6: Create Policy Engine
Creates an AgentCore Policy Engine that will evaluate all requests against defined policies.

### Step 7: Define Cedar Policy
Creates a Cedar policy that enforces business rules. The default policy allows refunds only if the amount is less than $1,000:

```cedar
permit(
  principal, 
  action == AgentCore::Action::"RefundTarget___process_refund", 
  resource == AgentCore::Gateway::"<gateway-arn>"
) when { 
  context.input.amount < 1000 
};
```

### Step 8: Attach Policy Engine to Gateway
Attaches the Policy Engine to the Gateway in **ENFORCE** mode, meaning all requests will be evaluated and blocked if they violate the policy.

### Step 9: Save Configuration
Saves all the configuration details (gateway URL, policy IDs, credentials, etc.) to `config.json` for use by other scripts.

## 🧪 How to Use

### 1. Setup
Run the setup script to create all resources:

```bash
cd agentcore-policy-quickstart
python setup_policy.py
```

This will create:
- AWS Gateway with OAuth authentication
- Lambda function with refund tool
- Policy Engine with refund limit rules
- `config.json` with all configuration details

### 2. Test
Test the policy enforcement:

```bash
python test_policy.py
```

This script runs two tests:
- **Test 1**: Refund $500 → ✅ Should be **ALLOWED** (under the $1,000 limit)
- **Test 2**: Refund $1,500 → ❌ Should be **DENIED** (exceeds the $1,000 limit)

### 3. Cleanup
When done, clean up all AWS resources:

```bash
python cleanup_policy.py
```

This removes the Gateway, Policy Engine, Lambda function, and Cognito resources.

## 🔑 Key Concepts

### AgentCore Gateway
A secure entry point that routes agent requests to backend tools while enforcing policies.

### Policy Engine
Evaluates all requests against Cedar policies before allowing them to proceed to the target tools.

### Cedar Policies
Declarative authorization policies that define who can do what and under what conditions.

### MCP (Model Context Protocol)
A standardized protocol for agent-tool communication that the gateway implements.

## 📋 Requirements

- AWS Account with appropriate permissions
- Python 3.13 or compatible version
- `bedrock_agentcore_starter_toolkit` package
- `boto3` for AWS SDK
- `requests` for HTTP calls

## 🛡️ Security

The setup includes:
- OAuth 2.0 authentication via AWS Cognito
- IAM role-based access control
- Policy-based authorization using Cedar
- Secure token management

## 📝 Configuration

The generated `config.json` contains:
- Gateway URL and identifiers
- Policy Engine details
- OAuth client credentials
- Region settings
- Configured refund limit

## 🎓 Learning Outcomes

By exploring this project, you'll understand:
1. How to implement fine-grained access control for AI agents
2. How to use Cedar policies for authorization
3. How to integrate AWS Lambda with AgentCore Gateway
4. How to test policy enforcement in agent systems
5. Best practices for securing agent-tool interactions

## 📚 Resources

- [AWS AgentCore Documentation](https://aws.amazon.com/bedrock/)
- [Cedar Policy Language](https://www.cedarpolicy.com/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

---

**Note**: This is a demonstration/testing repository. Modify the refund limit and policies in `setup_policy.py` to match your specific use case.

