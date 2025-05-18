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