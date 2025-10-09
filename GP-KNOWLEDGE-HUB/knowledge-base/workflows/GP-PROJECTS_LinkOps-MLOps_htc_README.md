# HTC (High Throughput Computing) Service

## Overview
The HTC service is an AI agent designed for managing high-throughput computing workloads, job scheduling, resource allocation, and cluster management in distributed computing environments.

## Service Structure

### Directory Layout
```
htc/
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container configuration
├── keywords.json              # Service keywords and tags
├── logic/                     # Core business logic
│   ├── __init__.py
│   ├── job_scheduler.py       # Job scheduling and management
│   ├── resource_manager.py    # Resource allocation and monitoring
│   └── cluster_manager.py     # Cluster scaling and optimization
├── resources/                 # Knowledge resources
│   ├── __init__.py
│   ├── job_scheduling.json    # Job scheduling knowledge
│   └── cluster_management.json # Cluster management knowledge
├── tools/                     # Executable tools
│   ├── __init__.py
│   ├── job_scheduler.yaml     # Job scheduling tool
│   └── cluster_scaler.yaml    # Cluster scaling tool
├── responsibilities/          # Role definitions
│   ├── __init__.py
│   └── role_duties.md         # Detailed role responsibilities
└── routers/                   # API route handlers
    └── __init__.py
```

## API Endpoints

### Job Management
- `POST /job/schedule` - Schedule a new HTC job
- `GET /job/{job_id}/status` - Get job status and progress
- `POST /job/{job_id}/cancel` - Cancel a running job

### Resource Management
- `POST /resources/allocate` - Allocate computing resources
- `POST /resources/{allocation_id}/deallocate` - Deallocate resources
- `GET /resources/status` - Get overall resource utilization

### Cluster Management
- `POST /cluster/manage` - Scale or optimize cluster
- `GET /cluster/{cluster_name}/health` - Get cluster health metrics

### Health and Status
- `GET /health` - Service health check
- `GET /` - Service information

## Key Features

### Job Scheduling
- Priority-based job scheduling (1-10 scale)
- Support for job dependencies
- Multiple job types (batch, interactive, streaming)
- Real-time job monitoring and progress tracking
- Job cancellation and cleanup

### Resource Management
- Dynamic resource allocation (CPU, memory, GPU, storage)
- Resource utilization monitoring
- Automatic resource optimization
- Capacity planning and forecasting

### Cluster Management
- Intelligent auto-scaling based on workload demand
- Multi-metric health monitoring
- Performance optimization
- Graceful scaling with resource draining

### Performance Optimization
- Throughput maximization
- Latency minimization
- Cost optimization
- Automated performance tuning

## Naming Conventions

The service follows the established naming conventions from the LinkOps platform:

### Files and Directories
- **snake_case** for Python files and directories
- **kebab-case** for service names and URLs
- **PascalCase** for class names
- **UPPER_CASE** for constants

### API Endpoints
- RESTful design with resource-based URLs
- Consistent HTTP methods (GET, POST, PUT, DELETE)
- Standard response formats with status codes

### Configuration
- Environment-based configuration
- Docker containerization
- Health checks and monitoring

## Dependencies

### Core Dependencies
- `fastapi>=0.109.1` - Web framework
- `uvicorn[standard]>=0.29.0` - ASGI server
- `pydantic>=2.7.1` - Data validation
- `aiohttp==3.9.1` - Async HTTP client
- `celery>=5.3.0` - Task queue
- `redis>=4.5.0` - Caching and message broker

### Development Dependencies
- `python-multipart>=0.0.19` - File uploads
- `python-jose[cryptography]==3.3.0` - JWT handling
- `passlib[bcrypt]==1.7.4` - Password hashing
- `python-dotenv==1.0.0` - Environment variables

## Deployment

### Docker
```bash
# Build the image
docker build -t htc-service .

# Run the container
docker run -p 8000:8000 htc-service
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Integration

The HTC service integrates with:
- **LinkOps Platform** - Main platform integration
- **Job Schedulers** - SLURM, PBS, SGE compatibility
- **Cloud Providers** - AWS, Azure, GCP support
- **Monitoring** - Prometheus, Grafana integration
- **Container Orchestration** - Kubernetes support

## Monitoring and Observability

### Metrics
- Job throughput and completion rates
- Resource utilization and efficiency
- Cluster health and performance
- API response times and error rates

### Logging
- Structured logging with correlation IDs
- Error tracking and debugging
- Performance monitoring
- Audit trails

## Security

### Authentication
- JWT-based authentication
- Role-based access control
- API key management

### Authorization
- Resource-level permissions
- Job ownership validation
- Cluster access control

### Data Protection
- Encrypted data transmission
- Secure resource allocation
- Audit logging

## Future Enhancements

### Planned Features
- Advanced job scheduling algorithms
- Machine learning-based optimization
- Multi-cloud resource management
- Real-time cost optimization
- Advanced monitoring and alerting

### Scalability Improvements
- Horizontal scaling support
- Load balancing enhancements
- Database optimization
- Caching improvements

## Contributing

### Development Guidelines
- Follow PEP 8 coding standards
- Write comprehensive tests
- Update documentation
- Use type hints
- Implement error handling

### Testing
- Unit tests for all logic components
- Integration tests for API endpoints
- Performance testing
- Security testing

## Support

For issues and questions:
- Check the documentation
- Review the API reference
- Contact the development team
- Submit bug reports with detailed information 