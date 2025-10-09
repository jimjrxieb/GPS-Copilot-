# 🔮 LinkOps Platform Agent

A production-ready Go CLI agent for safely executing shell commands and runes with comprehensive validation, logging, and API integration.

## 🚀 Features

### ✅ **Core Capabilities**
- **Safe Command Execution** - Validates and sanitizes all commands
- **Rune Support** - Execute complex workflows from JSON configurations
- **Timeout Protection** - Configurable timeouts to prevent hanging processes
- **Comprehensive Logging** - Detailed execution logs with timestamps
- **JSON Output** - Structured results for API integration
- **Cross-Platform** - Built for Linux, macOS, and Windows

### 🛡️ **Safety Features**
- **Command Blacklisting** - Blocks dangerous commands (rm, shutdown, etc.)
- **Path Restrictions** - Only allows commands from trusted directories
- **Input Validation** - Validates command structure and parameters
- **Error Handling** - Graceful failure handling with detailed error messages

### 🔧 **Integration Ready**
- **API Endpoints** - RESTful API for remote execution
- **Background Processing** - Asynchronous execution with status tracking
- **Result Storage** - Persistent storage of execution results
- **Health Monitoring** - Built-in health checks and monitoring

## 📦 Installation

### Quick Start
```bash
# Build the agent
./build.sh

# Install globally
cd build
./install.sh

# Test installation
platform_agent --help
```

### Manual Build
```bash
# Build for current platform
go build -o platform_agent platform_agent.go

# Cross-compile for multiple platforms
GOOS=linux GOARCH=amd64 go build -o platform_agent-linux-amd64 platform_agent.go
GOOS=darwin GOARCH=amd64 go build -o platform_agent-darwin-amd64 platform_agent.go
GOOS=windows GOARCH=amd64 go build -o platform_agent-windows-amd64.exe platform_agent.go
```

## 🎯 Usage

### Single Command Execution
```bash
# Execute a simple command
platform_agent "kubectl get pods"

# Execute with output
platform_agent "docker ps -a"

# Execute system commands
platform_agent "uname -a"
```

### Rune Execution
```bash
# Execute a rune configuration
platform_agent --rune examples/deployment-rune.json

# Execute system info rune
platform_agent --rune examples/system-info-rune.json

# Execute cleanup rune
platform_agent --rune examples/cleanup-rune.json
```

### API Integration
```bash
# Start the MLOps platform (includes rune executor API)
cd ../../mlops/mlops_platform
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Execute rune via API
curl -X POST http://localhost:8000/rune/execute \
  -H "Content-Type: application/json" \
  -d '{
    "commands": ["kubectl get pods", "docker ps"],
    "name": "API Test",
    "description": "Testing API integration"
  }'

# Check execution status
curl http://localhost:8000/rune/status/{execution_id}
```

## 📋 Rune Configuration

### Basic Rune Structure
```json
{
  "name": "My Rune",
  "description": "Description of what this rune does",
  "commands": [
    "kubectl get pods",
    "docker ps",
    "echo 'Hello World'"
  ],
  "validation": {
    "allowed_commands": ["kubectl", "docker", "echo"],
    "denied_commands": ["rm", "shutdown"],
    "timeout_seconds": 300,
    "stop_on_failure": true
  }
}
```

### Example Runes

#### Kubernetes Deployment Rune
```json
{
  "name": "Kubernetes Deployment",
  "description": "Deploy application to Kubernetes",
  "commands": [
    "kubectl create namespace test",
    "kubectl apply -f deployment.yaml",
    "kubectl rollout status deployment/app"
  ],
  "validation": {
    "timeout_seconds": 300,
    "stop_on_failure": true
  }
}
```

#### System Information Rune
```json
{
  "name": "System Info",
  "description": "Gather system information",
  "commands": [
    "uname -a",
    "df -h",
    "free -h",
    "uptime"
  ],
  "validation": {
    "timeout_seconds": 60,
    "stop_on_failure": false
  }
}
```

## 🔧 Configuration

### Agent Configuration File (`agent_config.json`)
```json
{
  "log_file": "platform_agent.log",
  "allowed_paths": [
    "/usr/local/bin",
    "/usr/bin",
    "/bin"
  ],
  "denied_commands": [
    "rm",
    "shutdown",
    "dd",
    "mkfs"
  ],
  "max_timeout_seconds": 300,
  "environment": "production"
}
```

### Environment Variables
```bash
# Set custom configuration
export PLATFORM_AGENT_CONFIG=/path/to/config.json
export PLATFORM_AGENT_LOG_LEVEL=debug
export PLATFORM_AGENT_TIMEOUT=600
```

## 🧪 Testing

### Run All Tests
```bash
# Python test suite
python3 test_agent.py

# Go tests
go test ./...

# Integration tests
./test_agent.sh
```

### Manual Testing
```bash
# Test help
./platform_agent --help

# Test simple command
./platform_agent "echo 'test'"

# Test rune execution
./platform_agent --rune examples/system-info-rune.json

# Test API integration
curl http://localhost:8000/rune/health
```

## 🔌 API Reference

### Endpoints

#### Execute Rune
```http
POST /rune/execute
Content-Type: application/json

{
  "commands": ["command1", "command2"],
  "name": "Rune Name",
  "description": "Description",
  "timeout_seconds": 300
}
```

#### Get Execution Status
```http
GET /rune/status/{execution_id}
```

#### List Executions
```http
GET /rune/list
```

#### Execute Simple Command
```http
POST /rune/execute-simple
Content-Type: application/json

"kubectl get pods"
```

#### Health Check
```http
GET /rune/health
```

### Response Format
```json
{
  "execution_id": "abc123",
  "status": "completed",
  "progress": 100,
  "total_commands": 3,
  "completed_commands": 3,
  "results": [
    {
      "command": "kubectl get pods",
      "success": true,
      "output": "NAME READY STATUS...",
      "duration": "1.234s",
      "exit_code": 0
    }
  ],
  "created_at": "2024-01-01T12:00:00Z",
  "completed_at": "2024-01-01T12:01:00Z"
}
```

## 🔒 Security

### Command Validation
- **Path Restrictions** - Only allows commands from trusted directories
- **Command Blacklisting** - Blocks dangerous commands
- **Input Sanitization** - Validates command structure
- **Timeout Protection** - Prevents hanging processes

### Safe Commands
```bash
# ✅ Allowed
kubectl get pods
docker ps
echo "hello"
uname -a

# ❌ Blocked
rm -rf /
shutdown -h now
dd if=/dev/zero of=/dev/sda
mkfs.ext4 /dev/sda1
```

## 📊 Monitoring

### Log Files
- **Execution Logs** - `platform_agent.log`
- **Result Files** - `rune_results_*.json`
- **Error Logs** - Stderr output

### Health Checks
```bash
# Check agent health
./platform_agent --health

# Check API health
curl http://localhost:8000/rune/health
```

## 🚀 Production Deployment

### Docker Deployment
```dockerfile
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o platform_agent platform_agent.go

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/platform_agent .
CMD ["./platform_agent"]
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: platform-agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: platform-agent
  template:
    metadata:
      labels:
        app: platform-agent
    spec:
      containers:
      - name: agent
        image: platform-agent:latest
        ports:
        - containerPort: 8080
        securityContext:
          readOnlyRootFilesystem: true
          runAsNonRoot: true
```

## 🔧 Troubleshooting

### Common Issues

#### Command Not Found
```bash
# Check if command exists in PATH
which kubectl

# Verify allowed paths in config
cat agent_config.json
```

#### Permission Denied
```bash
# Check file permissions
ls -la platform_agent

# Make executable
chmod +x platform_agent
```

#### API Connection Issues
```bash
# Check if MLOps platform is running
curl http://localhost:8000/health

# Check rune executor health
curl http://localhost:8000/rune/health
```

### Debug Mode
```bash
# Enable debug logging
export PLATFORM_AGENT_DEBUG=true
./platform_agent "command"

# Verbose output
./platform_agent --verbose "command"
```

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository>
cd tools/agents

# Install dependencies
go mod tidy

# Run tests
go test ./...

# Build
go build -o platform_agent platform_agent.go
```

### Code Style
- Follow Go conventions
- Add tests for new features
- Update documentation
- Use meaningful commit messages

## 📄 License

This project is part of the LinkOps MLOps Platform and follows the same license terms.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `platform_agent.log`
3. Test with the provided examples
4. Check the API health endpoint

---

**Status**: ✅ **Production Ready** - The Platform Agent is fully functional and ready for enterprise deployment. 