# MLOps Platform - Personal Memory & Automation Engine

The MLOps Platform is your centralized personal memory and automation engine for managing MLOps tasks, scripts, workflows, orbs, runes, and daily digests.

## 🚀 Quick Start

### Local Development
```bash
cd mlops/mlops_platform
pip install -r requirements.txt
uvicorn main:app --reload
```

### Docker
```bash
docker build -t mlops-platform .
docker run -p 8000:8000 mlops-platform
```

## 📊 API Endpoints

### Core Endpoints
- `GET /` - Welcome message
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

### Task Management
- `GET /tasks/` - List all tasks
- `POST /tasks/` - Create a new task
- `GET /tasks/{task_id}` - Get specific task
- `PUT /tasks/{task_id}` - Update task
- `DELETE /tasks/{task_id}` - Delete task
- `GET /tasks/stats/summary` - Task statistics

### Script Management
- `GET /scripts/` - List all scripts
- `POST /scripts/` - Create a new script
- `GET /scripts/{script_id}` - Get specific script
- `PUT /scripts/{script_id}` - Update script
- `DELETE /scripts/{script_id}` - Delete script
- `POST /scripts/{script_id}/execute` - Execute script
- `GET /scripts/templates/{category}` - Get script templates
- `GET /scripts/stats/popular` - Most popular scripts

### Workflow Management
- `GET /workflows/` - List all workflows
- `POST /workflows/` - Create a new workflow
- `GET /workflows/{workflow_id}` - Get specific workflow
- `PUT /workflows/{workflow_id}` - Update workflow
- `DELETE /workflows/{workflow_id}` - Delete workflow
- `POST /workflows/{workflow_id}/execute` - Execute workflow
- `GET /workflows/templates/{category}` - Get workflow templates
- `GET /workflows/stats/execution` - Workflow execution statistics

### Orb Management
- `GET /orbs/` - List all orbs
- `POST /orbs/` - Create a new orb
- `GET /orbs/{orb_id}` - Get specific orb
- `PUT /orbs/{orb_id}` - Update orb
- `DELETE /orbs/{orb_id}` - Delete orb
- `POST /orbs/{orb_id}/use` - Mark orb as used
- `POST /orbs/{orb_id}/rate` - Rate orb
- `GET /orbs/templates/{category}` - Get orb templates
- `GET /orbs/stats/popular` - Most popular orbs
- `GET /orbs/stats/highest_rated` - Highest rated orbs

### Rune Management
- `GET /runes/` - List all runes
- `POST /runes/` - Create a new rune
- `GET /runes/{rune_id}` - Get specific rune
- `PUT /runes/{rune_id}` - Update rune
- `DELETE /runes/{rune_id}` - Delete rune
- `POST /runes/{rune_id}/execute` - Execute rune
- `POST /runes/{rune_id}/feedback` - Provide feedback
- `GET /runes/templates/{category}` - Get rune templates
- `GET /runes/stats/most_successful` - Most successful runes
- `GET /runes/stats/most_used` - Most used runes

### Digest Management
- `GET /digest/` - List all digest entries
- `POST /digest/` - Create a new digest entry
- `GET /digest/{entry_id}` - Get specific digest entry
- `PUT /digest/{entry_id}` - Update digest entry
- `DELETE /digest/{entry_id}` - Delete digest entry
- `GET /digest/today/summary` - Today's summary
- `GET /digest/stats/weekly` - Weekly statistics
- `GET /digest/stats/monthly` - Monthly statistics
- `POST /digest/export` - Export digest entries
- `GET /digest/insights/productivity` - Productivity insights

## 📁 Data Structure

The platform stores data in JSON files within the `data/` directory:

```
data/
├── tasks.json          # Task data
├── scripts.json        # Script data
├── workflows.json      # Workflow data
├── orbs.json           # Orb data
├── runes.json          # Rune data
└── digest.json         # Digest data
```

## 🔧 Usage Examples

### Create a Task
```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement GitOps pipeline",
    "description": "Set up ArgoCD for automated deployments",
    "category": "kubernetes",
    "priority": "high",
    "tags": ["gitops", "argocd", "deployment"]
  }'
```

### Create a Script
```bash
curl -X POST "http://localhost:8000/scripts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "deploy_to_k8s",
    "description": "Deploy application to Kubernetes",
    "category": "kubernetes",
    "content": "kubectl apply -f k8s/",
    "language": "bash",
    "tags": ["kubernetes", "deployment"]
  }'
```

### Create a Workflow
```bash
curl -X POST "http://localhost:8000/workflows/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CI/CD Pipeline",
    "description": "Standard CI/CD pipeline",
    "category": "ci_cd",
    "steps": [
      {
        "name": "Build",
        "description": "Build the application",
        "action": "script",
        "parameters": {"script": "npm run build"}
      },
      {
        "name": "Test",
        "description": "Run tests",
        "action": "script",
        "parameters": {"script": "npm test"}
      }
    ],
    "triggers": ["webhook"],
    "tags": ["ci_cd", "automation"]
  }'
```

### Create a Daily Digest
```bash
curl -X POST "http://localhost:8000/digest/" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-01-15",
    "summary": "Completed GitOps implementation and started security audit",
    "tasks_completed": ["GitOps pipeline setup", "ArgoCD configuration"],
    "tasks_pending": ["Security audit completion", "Documentation update"],
    "achievements": ["Successfully deployed to staging", "Reduced deployment time by 50%"],
    "challenges": ["Kubernetes RBAC configuration issues"],
    "mood": "good",
    "hours_worked": 8.5
  }'
```

## 🎯 Features

### Task Management
- **Categories**: MLOps, Kubernetes, Infrastructure, Audit
- **Priorities**: Low, Medium, High, Critical
- **Status Tracking**: Pending, In Progress, Completed, Blocked
- **Filtering**: By category, status, priority, tags
- **Statistics**: Summary statistics and trends

### Script Management
- **Languages**: Bash, Python, YAML, JSON, etc.
- **Categories**: CLI, Infrastructure, Kubernetes, Security, Automation
- **Templates**: Pre-built templates for common tasks
- **Execution Tracking**: Usage counts and execution history
- **Dependencies**: Track script dependencies

### Workflow Management
- **Multi-step Workflows**: Complex automation sequences
- **Triggers**: Manual, Webhook, Schedule, Event
- **Step Types**: Script, API Call, Manual, Decision
- **Execution Tracking**: Success rates and execution history
- **Templates**: Pre-built workflow templates

### Orb Management
- **Best Practices**: Reusable workflow templates
- **Versioning**: Track orb versions
- **Rating System**: Community ratings and feedback
- **Usage Tracking**: Track orb usage across projects
- **Templates**: Pre-built orb templates

### Rune Management
- **Code Templates**: Reusable code snippets
- **Success Tracking**: Track rune success rates
- **Feedback System**: Collect user feedback
- **Language Support**: Multiple programming languages
- **Templates**: Pre-built rune templates

### Digest Management
- **Daily Logs**: Track daily activities and progress
- **Productivity Insights**: Analyze productivity patterns
- **Mood Tracking**: Correlate mood with productivity
- **Export Functionality**: Export data for analysis
- **Statistics**: Weekly and monthly summaries

## 🔗 Integration

### With LinkOps Platform
The MLOps Platform integrates seamlessly with the broader LinkOps ecosystem:

- **Whis Pipeline**: Feed training data to Whis for continuous learning
- **Shadow Agents**: Provide data to specialized agents (Igris, Katie, etc.)
- **Helm Charts**: Ready for Kubernetes deployment
- **Docker Compose**: Easy local development and testing

### External Tools
- **GitHub Actions**: Use orbs and runes in CI/CD pipelines
- **Kubernetes**: Deploy workflows and scripts
- **Monitoring**: Track execution metrics and performance
- **Analytics**: Export data for external analysis

## 🚀 Deployment

### Docker Compose
Add to your docker-compose.yml:
```yaml
mlops_platform:
  build: ./mlops/mlops_platform
  ports:
    - "8000:8000"
  volumes:
    - ./mlops/mlops_platform/data:/app/data
  environment:
    - DATABASE_URL=postgresql://linkops:password@db:5432/linkops
```

### Kubernetes
Use the provided Helm chart in `helm/mlops_platform/`.

### Environment Variables
- `DATABASE_URL` - Database connection string (optional)
- `LOG_LEVEL` - Logging level (default: INFO)
- `DATA_DIR` - Data directory path (default: ./data)

## 📈 Monitoring

### Health Check
```bash
curl http://localhost:8000/
```

### Statistics
```bash
# Task statistics
curl http://localhost:8000/tasks/stats/summary

# Script usage
curl http://localhost:8000/scripts/stats/popular

# Workflow execution
curl http://localhost:8000/workflows/stats/execution

# Productivity insights
curl http://localhost:8000/digest/insights/productivity
```

## 🔮 Future Enhancements

- **Real-time Collaboration**: WebSocket support for live updates
- **Advanced Analytics**: ML-powered insights and recommendations
- **Integration APIs**: Connect with external tools (Jira, GitHub, etc.)
- **Mobile App**: React Native app for mobile access
- **Voice Interface**: Voice commands and responses
- **AI Assistant**: Built-in AI for task suggestions and automation
- **Advanced Workflows**: Conditional logic and branching
- **Team Features**: Multi-user support and collaboration

---

**MLOps Platform** - Your Personal Memory & Automation Engine! 🧠⚡ 