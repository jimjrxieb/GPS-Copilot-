# Whis WebScraper - Intelligence Harvester

Whis WebScraper is the dedicated intelligence harvester for the Whis training ecosystem. It scrapes external sources and agent logs, then sends the data to `whis_sanitize` for processing and training queue integration.

## 🎯 **Purpose**

Whis WebScraper serves as Whis's personal research spider, continuously gathering intelligence from:

- **🌍 Web Sources**: Dev blogs, K8s docs, Terraform guides
- **📊 GitHub Trending**: Popular repositories and tools
- **📝 Agent Logs**: Intelligence patterns from LinkOps agents
- **🔄 Auto-Reloop**: Re-feed findings to training queue

## 🏗️ **Architecture**

```
External Sources ↴
whis_webscraper/
├── scrape_sources.py      # Web scraping (blogs, GitHub, docs)
├── scrape_agent_logs.py   # Agent log intelligence
├── send_to_sanitize.py    # Whis sanitize integration
└── main.py               # FastAPI application

Data Flow:
Web/Logs → WebScraper → Format → whis_sanitize → Training Queue
```

## 🚀 **Quick Start**

### Local Development

```bash
# Clone and setup
cd LinkOps-MLOps/shadows/whis_webscraper
pip install -r requirements.txt

# Run locally
uvicorn main:app --host 0.0.0.0 --port 8009 --reload
```

### Docker Deployment

```bash
# Build and run
docker build -t whis-webscraper .
docker run -p 8009:8009 whis-webscraper
```

## 🔌 **API Endpoints**

### Health Check
```bash
GET /health
```

### Complete Intelligence Scraping
```bash
POST /scrape/intelligence
{
  "sources": ["blogs", "github", "kubernetes_docs", "terraform_guides", "agent_logs"],
  "hours_back": 24,
  "send_to_sanitize": true,
  "auto_process": true
}
```

### Web Sources Only
```bash
POST /scrape/web_sources?hours_back=24&send_to_sanitize=true
```

### Agent Logs Only
```bash
POST /scrape/agent_logs?hours_back=24&send_to_sanitize=true
```

### Individual Sources
```bash
GET /scrape/blogs?hours_back=24&send_to_sanitize=true
GET /scrape/github_trending?send_to_sanitize=true
```

### Reloop Findings
```bash
GET /reloop/{task_id}?send_to_sanitize=true
```

### Sanitize Integration
```bash
GET /sanitize/health
GET /sanitize/stats
```

### Capabilities
```bash
GET /capabilities
```

## 📊 **Supported Sources**

### Web Sources
- **Kubernetes Blog**: Latest K8s best practices
- **Terraform Blog**: Infrastructure as Code guides
- **DevOps Weekly**: Industry trends and tools
- **CNCF Blog**: Cloud native developments
- **Helm Blog**: Package management updates

### GitHub Trending
- **Kubernetes**: K8s-related repositories
- **Terraform**: Infrastructure tools
- **Helm**: Package management
- **MLOps**: Machine learning operations

### Agent Logs
- **Katie**: Kubernetes operations patterns
- **Igris**: Infrastructure analysis insights
- **James**: AI assistant interactions
- **FickNury**: ML deployment patterns
- **Whis**: Training and processing patterns

## 🔧 **Configuration**

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SANITIZE_SERVICE_URL` | `http://whis_sanitize:8003` | Whis sanitize service URL |
| `LOGS_BASE_PATH` | `/app/logs` | Base path for agent logs |
| `SCRAPE_INTERVAL` | `3600` | Auto-scrape interval (seconds) |

### Scraping Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `hours_back` | `24` | How far back to scrape |
| `send_to_sanitize` | `true` | Auto-send to sanitize |
| `auto_process` | `true` | Auto-process in sanitize |

## 🧪 **Testing**

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_whis_webscraper.py::TestIntelligenceScraping
pytest tests/test_whis_webscraper.py::TestWebSourcesScraping
pytest tests/test_whis_webscraper.py::TestAgentLogScraping

# Run with coverage
pytest --cov=. tests/
```

## 🔄 **Integration with Whis Ecosystem**

### Data Flow
1. **Scrape**: Gather intelligence from multiple sources
2. **Format**: Standardize data for Whis processing
3. **Send**: Push to `whis_sanitize` for cleaning
4. **Queue**: Auto-add to Whis training queue
5. **Reloop**: Re-feed specific findings as needed

### Whis Sanitize Integration
```python
# Example: Send scraped data to sanitize
sanitize_sender = WhisSanitizeSender()
results = sanitize_sender.send_batch_to_sanitize(scraped_data)
```

### Training Queue Integration
- Automatically adds scraped content to Whis training queue
- Maintains data lineage and source tracking
- Supports priority-based processing

## 📈 **Monitoring & Observability**

### Health Checks
- **Service Health**: `/health` endpoint
- **Sanitize Health**: `/sanitize/health` endpoint
- **Integration Status**: Continuous monitoring

### Metrics
- Scraping success rates
- Source-specific metrics
- Sanitize integration metrics
- Training queue integration

### Logging
- Structured JSON logging
- Source tracking and lineage
- Error analysis and insights

## 🔒 **Security**

### Web Scraping
- Respectful rate limiting
- User-Agent identification
- Error handling and retries

### Data Privacy
- No sensitive data collection
- Public sources only
- Secure transmission to sanitize

### Container Security
- Non-root user execution
- Minimal attack surface
- Regular security updates

## 🚀 **Production Deployment**

### Docker Compose
```yaml
whis_webscraper:
  build: ./shadows/whis_webscraper
  ports:
    - "8009:8009"
  environment:
    - SANITIZE_SERVICE_URL=http://whis_sanitize:8003
  volumes:
    - ./logs:/app/logs
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: whis-webscraper
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: whis-webscraper
        image: whis-webscraper:latest
        ports:
        - containerPort: 8009
```

## 🔄 **Auto-Scraping Schedule**

### Recommended Schedule
- **Web Sources**: Every 6 hours
- **GitHub Trending**: Every 12 hours  
- **Agent Logs**: Every hour
- **Full Intelligence**: Daily

### Cron Job Example
```bash
# Daily full intelligence gathering
0 2 * * * curl -X POST http://whis-webscraper:8009/scrape/intelligence

# Hourly agent log scraping
0 * * * * curl -X POST http://whis-webscraper:8009/scrape/agent_logs
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 **License**

MIT License - see LICENSE file for details

## 🆘 **Support**

- **Documentation**: [LinkOps Docs](https://docs.linkops.local)
- **Issues**: [GitHub Issues](https://github.com/shadow-link-industries/linkops-mlops/issues)
- **Discussions**: [GitHub Discussions](https://github.com/shadow-link-industries/linkops-mlops/discussions)

---

**Whis WebScraper** - Your Intelligence Harvester for Whis Training 🕷️✨ 