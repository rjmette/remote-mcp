# Remote MCP Memory Server on AWS

This repository contains the resources and instructions for deploying a [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/servers) Memory server on AWS.

## Overview

The Model Context Protocol (MCP) is a protocol for contextual message passing between LLMs. This project focuses on deploying the memory implementation of an MCP server to AWS, following the guidelines from [Collabnix's article](https://collabnix.com/how-to-build-and-host-your-own-mcp-servers-in-easy-steps/).

## Prerequisites

- AWS Account
- AWS CLI configured with appropriate permissions
- SSH key pair for EC2 access (`MyKeyPair3` in this example)

## Deployment Steps

### 1. Create Security Group

```bash
aws ec2 create-security-group --group-name mcp-server-sg --description "Security group for MCP server" --vpc-id vpc-031bc219c72e0d1fe
```

Add inbound rules for SSH (port 22) and MCP server (port 8000):

```bash
aws ec2 authorize-security-group-ingress --group-id sg-00e2957f15dfd982b --protocol tcp --port 8000 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id sg-00e2957f15dfd982b --protocol tcp --port 22 --cidr 0.0.0.0/0
```

### 2. Launch EC2 Instance

```bash
aws ec2 run-instances --image-id ami-09f4814ae750baed6 --instance-type t2.micro --key-name MyKeyPair3 --security-group-ids sg-00e2957f15dfd982b --subnet-id subnet-038fe817a8e9f0f1b --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=mcp-memory-server}]'
```

### 3. Create User Data Script

Create a file named `user-data.sh` with the following content:

```bash
#!/bin/bash
yum update -y
yum install -y docker git
service docker start
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone the MCP servers repository
su - ec2-user -c "git clone https://github.com/modelcontextprotocol/servers.git ~/mcp-servers"

# Run the memory server using Docker Compose
su - ec2-user -c "cd ~/mcp-servers && docker-compose -f docker-compose.memory.yaml up -d"
```

### 4. Apply User Data to Instance

First, stop the instance:

```bash
aws ec2 stop-instances --instance-ids i-0cf2c96f32d062d77
aws ec2 wait instance-stopped --instance-ids i-0cf2c96f32d062d77
```

Encode and apply the user data:

```bash
cat user-data.sh | base64 > user-data-encoded.txt
aws ec2 modify-instance-attribute --instance-id i-0cf2c96f32d062d77 --attribute userData --value file://user-data-encoded.txt
```

Start the instance again:

```bash
aws ec2 start-instances --instance-ids i-0cf2c96f32d062d77
aws ec2 wait instance-running --instance-ids i-0cf2c96f32d062d77
```

### 5. Get Instance Public IP

```bash
aws ec2 describe-instances --instance-ids i-0cf2c96f32d062d77 --query "Reservations[0].Instances[0].PublicIpAddress"
```

## Connecting to Your MCP Server

### SSH Access

```bash
ssh -i /path/to/MyKeyPair3.pem ec2-user@54.242.99.144
```

### MCP Server Access

The MCP Memory server will be available at:

```
http://54.242.99.144:8000
```

## Testing Your MCP Server

A Python script is provided to test if your MCP Memory server is working correctly. The script stores a message and then retrieves it to verify functionality.

### Prerequisites for Testing

- Python 3.6+
- requests library (`pip install -r requirements.txt`)

### Using the Test Script

```bash
# Install dependencies
pip install -r requirements.txt

# Run the test script with your server URL
python test_mcp_server.py http://54.242.99.144:8000
```

The script will:

1. Generate a unique conversation ID
2. Store a test message on the server
3. Retrieve the stored message
4. Verify the content matches

Example output:

```
Testing MCP Memory Server at: http://54.242.99.144:8000
Using conversation ID: 12345678-1234-5678-1234-567812345678

=== Step 1: Storing a message ===
POST http://54.242.99.144:8000/memory/12345678-1234-5678-1234-567812345678
Data: {
  "role": "user",
  "content": "Test message from MCP client",
  "metadata": {
    "timestamp": 1621234567.89
  }
}
Status: 200
Response: {"status":"success"}
✅ Message stored successfully

=== Step 2: Retrieving messages ===
GET http://54.242.99.144:8000/memory/12345678-1234-5678-1234-567812345678
Status: 200
Retrieved 1 message(s)
Response: [
  {
    "role": "user",
    "content": "Test message from MCP client",
    "metadata": {
      "timestamp": 1621234567.89
    }
  }
]
✅ Message content verified

=== Test Completed Successfully ===
```

## Troubleshooting

If you need to check if the MCP server is running properly on the EC2 instance:

1. SSH into the instance
2. Run `docker ps` to check if the container is running
3. Check logs with `docker logs <container_id>`

## Resources

- [MCP Servers GitHub Repository](https://github.com/modelcontextprotocol/servers)
- [How to Build and Host Your Own MCP Servers](https://collabnix.com/how-to-build-and-host-your-own-mcp-servers-in-easy-steps/)
