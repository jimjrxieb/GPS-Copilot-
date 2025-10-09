# LinkOps Complete Learning Pipeline

## 🧠 Overview

The LinkOps Complete Learning Pipeline is a sophisticated AI-powered task routing, learning, and agent enhancement system that continuously improves automation capabilities through structured knowledge representation (ORBs) and executable action patterns (RUNEs).

## 🏗️ Complete Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Task Input    │───▶│ FickNury Router │───▶│ Confidence      │
│   (James GUI)   │    │                 │    │ Evaluation      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┬─────────────────┬─────────────────┐
│   High Conf.    │  Medium Conf.   │   Low Conf.     │
│   (≥0.95)       │   (≥0.7)        │   (<0.7)        │
│                 │                 │                 │
│ Direct Agent    │ Whis Learning   │ Manual Review   │
│ Assignment      │                 │                 │
│                 │                 │                 │
│ • Katie Logic   │ • Whis Data     │ • James Logic   │
│ • Igris Logic   │ • Sanitization  │ • Manual Export │
│ • Audit Logic   │ • Training      │ • CSV Tracking  │
└─────────────────┴─────────────────┴─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Training Queue  │───▶│ Whis Smithing   │───▶│ ORBs & RUNEs    │
│ (CSV)           │    │ (Knowledge Gen) │    │ Generation      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Agent Enhancement│◀───│ Whis Enhance    │◀───│ ORB/RUNE        │
│ (Capability     │    │ (Agent Upgrade) │    │ Application     │
│  Matrix)        │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Service Components

### 1. **FickNury Evaluator** (`ficknury_evaluator`)
- **Port**: 8008
- **Purpose**: Task evaluation and intelligent routing
- **Key Files**: `task_router.py`, `main.py`
- **Endpoints**:
  - `POST /evaluate` - Evaluate and route tasks
  - `POST /api/evaluate` - Legacy batch evaluation
  - `GET /health` - Health check

### 2. **James Logic** (`james_logic`)
- **Port**: 8002
- **Purpose**: Manual task review and export
- **Key Files**: `manual_task_export.py`, `main.py`
- **Endpoints**:
  - `POST /manual/manual-review` - Save manual tasks
  - `POST /manual/complete-task` - Mark tasks complete
  - `GET /manual/pending-tasks` - List pending tasks
  - `GET /manual/training-stats` - Training statistics

### 3. **Whis Data Input** (`whis_data_input`)
- **Port**: 8004
- **Purpose**: Learning queue management and task ingestion
- **Key Files**: `main.py`, `training_queue.csv`
- **Endpoints**:
  - `POST /task` - Receive tasks from James
  - `POST /learn` - Add tasks to learning queue
  - `GET /health` - Health check

### 4. **Whis Sanitize** (`whis_sanitize`)
- **Port**: 8003
- **Purpose**: Task input sanitization and cleaning
- **Key Files**: `main.py`
- **Endpoints**:
  - `POST /sanitize` - Sanitize task input
  - `GET /health` - Health check

### 5. **Whis Smithing** (`whis_smithing`)
- **Port**: 8005
- **Purpose**: ORB and RUNE generation from training data
- **Key Files**: `main.py`, `orbs.json`, `runes.json`
- **Endpoints**:
  - `POST /generate-orbs` - Generate ORBs from training queue
  - `POST /generate-runes` - Generate RUNEs from ORBs
  - `POST /process-training-queue` - Complete pipeline processing
  - `GET /orbs` - Get all ORBs
  - `GET /runes` - Get all RUNEs

### 6. **Whis Enhance** (`whis_enhance`)
- **Port**: 8006
- **Purpose**: Agent enhancement using ORBs and RUNEs
- **Key Files**: `main.py`, `enhancement_records.json`
- **Endpoints**:
  - `POST /enhance-agent` - Enhance specific agent
  - `POST /bulk-enhance` - Enhance multiple agents
  - `GET /enhancement-history/{agent_id}` - Get agent history
  - `GET /capability-matrix` - Get capability matrix

## 📊 Data Structures

### Training Queue CSV
```csv
task_id,title,description,tools_used,commands,solution_summary,status,tags,confidence,agent,created_at,completed_at
TASK-001,Deploy Helm Chart,Deploy app using Helm,helm kubectl,helm install myapp,Successfully deployed,completed,kubernetes,0.95,katie_logic,2024-01-15T10:30:00,2024-01-15T11:15:00
```

### ORB (Orbital Knowledge Base)
```json
{
  "orb_id": "orb-kubernetes-20240115",
  "name": "Kubernetes Operations",
  "description": "Knowledge base for Kubernetes operations",
  "category": "kubernetes",
  "tags": ["helm", "kubectl", "deployment"],
  "knowledge_base": {
    "tools_used": ["helm", "kubectl"],
    "common_commands": ["helm install", "kubectl apply"],
    "success_patterns": ["Successfully deployed"],
    "task_count": 10,
    "success_rate": 0.9
  },
  "confidence": 0.9,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

### RUNE (Runnable Action Pattern)
```json
{
  "rune_id": "rune-orb-kubernetes-20240115",
  "name": "Execute Kubernetes Operations",
  "description": "Execute Kubernetes deployment operations",
  "orb_id": "orb-kubernetes-20240115",
  "action_type": "command_execution",
  "commands": ["helm install myapp ./chart"],
  "parameters": {
    "category": "kubernetes",
    "tools_required": ["helm", "kubectl"],
    "estimated_time": "5m",
    "risk_level": "medium"
  },
  "success_criteria": {
    "exit_code": 0,
    "output_contains": "success",
    "timeout": 300
  },
  "created_at": "2024-01-15T12:00:00Z"
}
```

## 🚀 Complete Workflow

### 1. **Task Submission**
```python
import requests

task = {
    "task_id": "TASK-001",
    "title": "Deploy Helm Chart",
    "description": "Deploy application using Helm chart",
    "priority": "high",
    "category": "deployment",
    "tags": ["helm", "kubernetes"]
}

response = requests.post("http://localhost:8008/evaluate", json=task)
evaluation = response.json()
```

### 2. **Task Routing**
- **High Confidence (≥0.95)**: Direct agent assignment
- **Medium Confidence (≥0.7)**: Whis learning queue
- **Low Confidence (<0.7)**: Manual review via James

### 3. **Learning Pipeline**
```python
# Manual task completion
solution = {
    "task_id": "TASK-001",
    "tools_used": ["helm", "kubectl"],
    "commands": ["helm install myapp ./chart"],
    "solution_summary": "Successfully deployed",
    "status": "completed",
    "tags": ["kubernetes", "helm"]
}

requests.post("http://localhost:8002/manual/complete-task", json=solution)
```

### 4. **Knowledge Generation**
```python
# Generate ORBs and RUNEs
response = requests.post("http://localhost:8005/process-training-queue")
result = response.json()
print(f"Generated {result['orbs_generated']} ORBs and {result['runes_generated']} RUNEs")
```

### 5. **Agent Enhancement**
```python
enhancement_request = {
    "agent_id": "katie_logic",
    "agent_type": "kubernetes",
    "current_capabilities": ["helm_deploy"],
    "target_improvements": ["security", "monitoring"],
    "context": {"environment": "production"}
}

response = requests.post("http://localhost:8006/enhance-agent", json=enhancement_request)
enhancement = response.json()["enhancement"]
```

## 🧪 Testing

### Run Complete Test Suite
```bash
python test_complete_pipeline.py
```

This will test:
- ✅ Service health checks
- ✅ Task submission and routing
- ✅ Manual task processing
- ✅ Learning queue functionality
- ✅ Task sanitization
- ✅ ORB/RUNE generation
- ✅ Agent enhancement
- ✅ Capability matrix generation

### Individual Service Tests
```bash
# Test task routing
curl -X POST http://localhost:8008/evaluate \
  -H "Content-Type: application/json" \
  -d '{"task_id":"TEST-001","title":"Deploy App","description":"Deploy application"}'

# Test manual task export
curl -X POST http://localhost:8002/manual/manual-review \
  -H "Content-Type: application/json" \
  -d '{"task_id":"MANUAL-001","title":"Complex Task","description":"Complex task description"}'

# Test ORB generation
curl -X POST http://localhost:8005/generate-orbs

# Test agent enhancement
curl -X POST http://localhost:8006/enhance-agent \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"katie_logic","agent_type":"kubernetes","current_capabilities":[],"target_improvements":["security"]}'
```

## 📈 Monitoring & Metrics

### Key Metrics
- **Task Processing Rate**: Tasks per minute
- **Confidence Distribution**: High/Medium/Low confidence ratios
- **Learning Efficiency**: ORBs/RUNEs generated per day
- **Agent Enhancement**: Capability improvements over time
- **Success Rates**: Task completion rates by agent

### Health Checks
```bash
# Check all services
for service in ficknury james whis_data whis_sanitize whis_smithing whis_enhance; do
  curl http://localhost:800$(echo $service | grep -o '[0-9]')/health
done
```

### Training Statistics
```bash
curl http://localhost:8002/manual/training-stats
```

## 🔮 Advanced Features

### 1. **Machine Learning Integration**
- Train models on completed tasks
- Predict confidence scores
- Suggest optimal agents

### 2. **Advanced Routing**
- Load balancing across agents
- Priority-based queuing
- SLA monitoring

### 3. **Analytics Dashboard**
- Real-time metrics
- Performance trends
- Learning progress

### 4. **Automated Deployment**
- Confidence threshold triggers
- Automatic agent scaling
- Self-healing capabilities

## 🛠️ Deployment

### Docker Compose
```bash
docker-compose up -d
```

### Kubernetes (Helm)
```bash
# Install all services
helmfile apply

# Or install individually
helm install whis-logic ./helm/whis_logic --namespace linkops
helm install whis-smithing ./helm/whis_smithing --namespace linkops
helm install whis-enhance ./helm/whis_enhance --namespace linkops
```

### Environment Variables
```bash
# Required
POSTGRES_PASSWORD=your_password
KAFKA_BOOTSTRAP_SERVERS=kafka:29092

# Optional (for testing)
AWS_ACCESS_KEY_ID=dummy
AWS_SECRET_ACCESS_KEY=dummy
AWS_DEFAULT_REGION=us-east-1
OPENAI_API_KEY=sk-dummy
```

## 📚 API Documentation

### Swagger UI
- FickNury: http://localhost:8008/docs
- James: http://localhost:8002/docs
- Whis Data: http://localhost:8004/docs
- Whis Sanitize: http://localhost:8003/docs
- Whis Smithing: http://localhost:8005/docs
- Whis Enhance: http://localhost:8006/docs

## 🔄 Continuous Learning

The pipeline continuously improves through:

1. **Task Collection**: New tasks from various sources
2. **Pattern Recognition**: Identifying common patterns in successful tasks
3. **Knowledge Extraction**: Creating ORBs from task groups
4. **Action Generation**: Creating RUNEs from ORBs
5. **Agent Enhancement**: Applying knowledge to improve agents
6. **Feedback Loop**: Using enhanced agents to handle more tasks

## 🎯 Success Metrics

- **Task Automation Rate**: Percentage of tasks handled automatically
- **Confidence Improvement**: Average confidence scores over time
- **Agent Capability Growth**: Number of capabilities per agent
- **Learning Velocity**: Time from task to knowledge application
- **Success Rate**: Task completion success rates

---

**Built with ❤️ by Shadow Link Industries**

*The LinkOps Complete Learning Pipeline represents the future of intelligent automation, where systems learn, adapt, and improve continuously.* 