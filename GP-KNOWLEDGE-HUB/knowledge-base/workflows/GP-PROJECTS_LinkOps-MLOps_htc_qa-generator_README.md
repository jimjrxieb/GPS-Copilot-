# QA Generator Service

A comprehensive QA generation and scoring system that pulls content from multiple sources (Flowright, Grok, browser automation) and provides continuous learning capabilities through test history tracking and performance analysis.

## 🎯 Overview

The QA Generator service is designed to:
- **Generate QA questions** from multiple sources (Flowright, Grok, browser automation)
- **Score answers** with intelligent feedback and confidence calculation
- **Track learning progress** through comprehensive test history
- **Provide continuous improvement** through tag optimization and performance analysis
- **Integrate with external systems** like James-enhance and Ficknury

## 🏗️ Architecture

```
qa-generator/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── keywords.json          # Service keywords for categorization
├── qa_generators/         # QA source generators
│   ├── flowright.py       # Flowright platform integration
│   ├── grok.py           # Grok AI integration
│   └── browser.py        # Browser automation with Playwright
├── logic/                 # Core business logic
│   ├── qa_loop.py        # QA generation and scoring loop
│   ├── scoring.py        # Answer scoring and feedback
│   └── history.py        # Test history and learning metrics
├── evaluations/           # Evaluation and result logging
├── test_history/          # Long-term learning tracking
├── tools/                 # Automation tools and definitions
├── resources/             # Knowledge base and resources
├── responsibilities/      # Role duties and responsibilities
└── routers/              # API route handlers
```

## 🚀 Quick Start

### Local Development

```bash
# Clone and setup
cd LinkOps-Host/qa-generator
pip install -r requirements.txt

# Run locally
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker Deployment

```bash
# Build and run
docker build -t qa-generator .
docker run -p 8000:8000 qa-generator
```

## 🔌 API Endpoints

### Health Check
```bash
GET /health
```

### Generate QA Questions
```bash
POST /qa/generate
{
  "source": "combined",
  "topic": "kubernetes",
  "num_questions": 10,
  "difficulty_level": "medium",
  "include_context": true
}
```

### Score QA Answer
```bash
POST /qa/score
{
  "question_id": "q_123",
  "user_answer": "A Pod is the smallest deployable unit in Kubernetes",
  "expected_answer": "A Pod is the smallest deployable unit in Kubernetes that can contain one or more containers",
  "context": "Kubernetes basics",
  "difficulty": "medium"
}
```

### Log Test History
```bash
POST /qa/history
{
  "test_id": "test_123",
  "question_answers": [
    {
      "question_id": "q_1",
      "user_answer": "Answer 1",
      "score": 0.8,
      "confidence": 0.7
    }
  ],
  "performance_metrics": {
    "time_taken": 300,
    "accuracy": 0.8
  },
  "learning_objectives": ["kubernetes", "containers"]
}
```

### Run QA Loop
```bash
GET /qa/loop/run
```

### Get Metrics
```bash
GET /qa/metrics
```

## 🧠 Core Features

### 1. Multi-Source QA Generation
- **Flowright Integration**: Extract Q&A content from Flowright platform
- **Grok AI Integration**: Generate intelligent Q&A using Grok AI
- **Browser Automation**: Scrape Q&A content using Playwright
- **Combined Generation**: Generate from multiple sources simultaneously

### 2. Intelligent Answer Scoring
- **Multiple Scoring Criteria**: Exact match, partial match, semantic similarity
- **Confidence Calculation**: Calculate confidence scores based on answer quality
- **Constructive Feedback**: Provide actionable improvement suggestions
- **Difficulty Adjustment**: Adjust scoring based on question difficulty

### 3. Learning Loop Management
- **Attempt Tracking**: Monitor all QA generation and scoring attempts
- **Tag Improvement**: Continuously improve question tags based on performance
- **Performance Optimization**: Optimize algorithms based on historical data
- **Continuous Learning**: Adapt and improve based on results

### 4. Test History and Analytics
- **Long-term Tracking**: Maintain comprehensive test history
- **Performance Trends**: Analyze trends and identify improvement areas
- **Learning Metrics**: Calculate progress and provide recommendations
- **Strength/Weakness Analysis**: Identify user strengths and weaknesses

### 5. Integration Capabilities
- **James-enhance Integration**: Connect successful resources to James-enhance
- **Postgres Storage**: Persistent storage for test statistics
- **Ficknury Integration**: Compare category performance
- **RESTful APIs**: External integration support

## 📊 Supported Topics

### Technical Topics
- **Kubernetes**: Container orchestration and management
- **Docker**: Containerization and container management
- **DevOps**: CI/CD, automation, and infrastructure
- **Python**: Programming and development
- **Machine Learning**: AI, ML, and data science

### Difficulty Levels
- **Easy**: Basic concepts and fundamental knowledge
- **Medium**: Intermediate concepts and practical applications
- **Hard**: Advanced concepts and complex scenarios

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
FLOWRIGHT_API_KEY=your_flowright_api_key
GROK_API_KEY=your_grok_api_key
BROWSER_HEADLESS=true

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/qa_generator
REDIS_URL=redis://localhost:6379

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Dependencies
- **FastAPI**: Web framework for API development
- **Playwright**: Browser automation for web scraping
- **PostgreSQL**: Database for persistent storage
- **Redis**: Caching and session management
- **Pydantic**: Data validation and serialization

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_qa_generation.py

# Run with coverage
python -m pytest --cov=qa_generator tests/
```

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: Service interaction testing
- **API Tests**: Endpoint functionality testing
- **Performance Tests**: Load and stress testing

## 📈 Monitoring and Metrics

### Key Metrics
- **Question Generation Rate**: Questions generated per minute
- **Scoring Accuracy**: Accuracy of automated scoring
- **User Engagement**: User interaction with the system
- **Learning Progress**: Measurable learning improvements
- **System Performance**: Response times and reliability

### Health Checks
- **Service Health**: Overall service status
- **Database Connectivity**: Database connection status
- **External API Health**: Flowright, Grok, and browser status
- **Resource Usage**: CPU, memory, and disk usage

## 🔒 Security

### Security Features
- **Input Validation**: Comprehensive input validation and sanitization
- **Rate Limiting**: API rate limiting to prevent abuse
- **Authentication**: API key authentication for external integrations
- **Data Encryption**: Sensitive data encryption at rest and in transit
- **Audit Logging**: Comprehensive audit logging for security events

### Best Practices
- **Principle of Least Privilege**: Minimal required permissions
- **Secure Defaults**: Secure configuration defaults
- **Regular Updates**: Regular dependency and security updates
- **Vulnerability Scanning**: Automated vulnerability scanning
- **Security Monitoring**: Continuous security monitoring

## 🚀 Deployment

### Docker Deployment
```bash
# Build image
docker build -t qa-generator .

# Run container
docker run -d \
  --name qa-generator \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@db/qa_generator \
  qa-generator
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qa-generator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: qa-generator
  template:
    metadata:
      labels:
        app: qa-generator
    spec:
      containers:
      - name: qa-generator
        image: qa-generator:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: qa-generator-secrets
              key: database-url
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Standards
- **Python**: Follow PEP 8 style guidelines
- **Documentation**: Maintain comprehensive documentation
- **Testing**: Maintain high test coverage
- **Security**: Follow security best practices
- **Performance**: Optimize for performance and scalability

## 📚 Documentation

### API Documentation
- **Swagger UI**: Interactive API documentation at `/docs`
- **OpenAPI Spec**: Machine-readable API specification
- **Postman Collection**: Ready-to-use API collection

### User Guides
- **Getting Started**: Quick start guide for new users
- **API Reference**: Comprehensive API reference
- **Integration Guide**: External system integration guide
- **Troubleshooting**: Common issues and solutions

## 🔮 Future Enhancements

### Planned Features
- **Advanced AI Integration**: Enhanced AI capabilities for question generation
- **Real-time Learning**: Real-time learning adaptation
- **Multi-language Support**: Support for multiple languages
- **Advanced Analytics**: Advanced analytics and reporting
- **Mobile Support**: Mobile-friendly interface

### Integration Opportunities
- **Learning Management Systems**: LMS platform integration
- **HR Systems**: Employee training integration
- **Assessment Platforms**: Certification platform integration
- **Analytics Platforms**: BI and analytics integration
- **Collaboration Tools**: Team collaboration integration

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- **Documentation**: Check the documentation first
- **Issues**: Create an issue on GitHub
- **Discussions**: Join discussions on GitHub
- **Email**: Contact the development team

---

**QA Generator Service** - Empowering continuous learning through intelligent QA generation and scoring. 