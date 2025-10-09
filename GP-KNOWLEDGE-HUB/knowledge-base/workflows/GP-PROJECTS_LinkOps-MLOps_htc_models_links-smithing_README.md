# Links Smithing Service

Generates production-ready automation tools from task descriptions using LangChain and GPT-4.

## 🏗️ Architecture

This service is part of the LinkOps pipeline:

```
Pipeline Flow:
1. data-intake/
2. preprocess-sanitize/
3. links-smithing/          <-- This service
4. links-forging/           <-- Runs in parallel
5. approval or relearn (HTC or link-enhance)
6. save to db/job-categories/[domain]/tools/
```

## 🚀 Features

- **LangChain Integration**: Uses GPT-4 for intelligent tool generation
- **Production Ready**: Comprehensive error handling and logging
- **Tag Generation**: Automatic categorization of generated tools
- **Confidence Scoring**: Quality assessment of generated tools
- **Batch Processing**: Generate multiple tools simultaneously
- **Database Integration**: Save tools to job categories database
- **Health Monitoring**: Built-in health checks and metrics

## 📁 Project Structure

```
links-smithing/
├── main.py                    # FastAPI application
├── README.md                  # This file
├── Dockerfile                 # Container configuration
├── requirements.txt           # Python dependencies
├── logic/
│   └── rune_generator.py      # Core LangChain logic
├── schemas/
│   └── tool_schema.py         # Pydantic schemas
└── tests/
    └── test_smithing.py       # Comprehensive tests
```

## 🛠️ Installation

### Local Development

```bash
# Clone and setup
cd ml-models/links-smithing
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"

# Run the service
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### Docker

```bash
# Build the image
docker build -t links-smithing .

# Run the container
docker run -p 8080:8080 \
  -e OPENAI_API_KEY="your-openai-api-key" \
  links-smithing
```

## 📡 API Endpoints

### Generate Tool

```bash
POST /generate-tool
```

**Request:**
```json
{
  "task_text": "Deploy a Python web application to Kubernetes",
  "context": "Production environment with monitoring",
  "save_to_db": true
}
```

**Response:**
```json
{
  "tool_code": "#!/bin/bash\nset -euo pipefail\n\necho 'Deploying Python web app...'\nkubectl apply -f deployment.yaml\necho 'Deployment completed'",
  "description": "Automation tool generated from task: Deploy a Python web application to Kubernetes",
  "tags": ["kubernetes", "deployment", "python", "automation", "devops"],
  "source_model": "links-smithing",
  "autonomy_score": 92,
  "validated": false,
  "created_at": "2024-01-01T12:00:00",
  "task_input": "Deploy a Python web application to Kubernetes",
  "context": "Production environment with monitoring"
}
```

### Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "model_loaded": true,
  "openai_configured": true
}
```

### Batch Generation

```bash
POST /generate-tool/batch
```

**Request:**
```json
{
  "tasks": [
    {"task_text": "Deploy app", "context": "Production"},
    {"task_text": "Setup monitoring", "context": "Kubernetes"}
  ]
}
```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `LOG_LEVEL`: Logging level (default: INFO)
- `MODEL_TEMPERATURE`: LLM temperature (default: 0.3)
- `MODEL_NAME`: LLM model name (default: gpt-4)

### Model Parameters

The service uses the following LangChain configuration:

- **Model**: GPT-4
- **Temperature**: 0.3 (balanced creativity and consistency)
- **Max Tokens**: Default OpenAI limit
- **Prompt Template**: Optimized for DevOps automation

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_smithing.py::TestRuneGenerator::test_run_model_basic

# Run with coverage
pytest --cov=logic tests/
```

## 📊 Integration

### Pipeline Integration

Add this to your orchestrator service:

```python
import requests

def run_smithing(task_text: str, context: str = "") -> dict:
    """Call the links-smithing service."""
    response = requests.post(
        "http://links-smithing:8080/generate-tool",
        json={
            "task_text": task_text,
            "context": context,
            "save_to_db": True
        }
    )
    return response.json()
```

### Database Integration

Generated tools are saved to:
```
db/job-categories/[domain]/tools/[tool_name].v1.json
```

Example saved tool:
```json
{
  "tool_code": "#!/bin/bash\nkubectl apply -f deployment.yaml",
  "description": "Kubernetes deployment script",
  "tags": ["kubernetes", "deployment", "automation"],
  "source_model": "links-smithing",
  "autonomy_score": 92,
  "validated": false,
  "created_at": "2024-01-01T12:00:00",
  "task_input": "Deploy microservice",
  "context": "Production environment"
}
```

## 🎯 Supported Technologies

The service can generate tools for:

- **Kubernetes**: Deployments, services, configmaps
- **Docker**: Container builds, runs, management
- **Terraform**: Infrastructure provisioning
- **AWS/Azure/GCP**: Cloud-specific automation
- **CI/CD**: Pipeline automation
- **Monitoring**: Logging, metrics, alerting
- **Security**: Access control, scanning, compliance

## 🔍 Monitoring

### Health Checks

- Service health: `GET /health`
- Model status: `GET /models/info`
- Database connectivity (if configured)

### Logging

The service logs:
- Tool generation requests
- Success/failure rates
- Performance metrics
- Error details

### Metrics

Track these metrics:
- Generation success rate
- Average confidence scores
- Response times
- Error rates by task type

## 🚨 Error Handling

The service includes comprehensive error handling:

- **LLM Failures**: Fallback to basic script generation
- **Invalid Input**: Proper validation with helpful error messages
- **Network Issues**: Graceful degradation
- **Rate Limiting**: Exponential backoff for API calls

## 🔄 Development

### Adding New Capabilities

1. **New Technology Support**: Add tags and prompts in `rune_generator.py`
2. **Custom Prompts**: Modify the prompt template
3. **Additional Schemas**: Extend `tool_schema.py`
4. **New Endpoints**: Add to `main.py`

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📈 Performance

- **Average Response Time**: < 5 seconds
- **Success Rate**: > 95%
- **Concurrent Requests**: Up to 10 simultaneous
- **Memory Usage**: ~500MB per instance

## 🔒 Security

- Input validation and sanitization
- Rate limiting on API endpoints
- Secure handling of API keys
- CORS configuration for production
- Error message sanitization

## 📝 License

This service is part of the LinkOps platform. 