# LinkOps Data Flow Diagram

## Complete Service Communication Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Input    │    │  Data Collector │    │   Sanitizer     │    │      Whis       │
│   (Frontend/    │───▶│   (Port 8001)   │───▶│   (Port 8002)   │───▶│   (Port 8003)   │
│    External)    │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │                       │
                                │                       │                       │
                                ▼                       ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                       │     Kafka       │    │  Training Data  │    │   FickNury      │
                       │   (Legacy)      │    │    Storage      │    │   (Port 8004)   │
                       │                 │    │                 │    │                 │
                       └─────────────────┘    └─────────────────┘    └─────────────────┘
                                                                               │
                                                                               ▼
                                                                      ┌─────────────────┐
                                                                      │   Agent         │
                                                                      │  Deployment     │
                                                                      │   (Katie/       │
                                                                      │  AuditGuard/    │
                                                                      │  Igris/etc.)    │
                                                                      └─────────────────┘

## Solution Entry Flow (Auto-Training)

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Solution Entry │    │  Data Collector │    │   Sanitizer     │    │      Whis       │
│  (#log:solution)│───▶│   (Port 8001)   │───▶│   (Port 8002)   │───▶│   (Port 8003)   │
│                 │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │                       │
                                │                       │                       │
                                ▼                       ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                       │   Solution      │    │  Enhanced       │    │  Auto-Training  │
                       │   Detection     │    │  Sanitization   │    │  + Rune Creation│
                       │                 │    │                 │    │                 │
                       └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Service Communication Details

### 1. Data Collector → Sanitizer
- **Endpoint**: `POST /api/collect`
- **Environment Variable**: `SANITIZER_URL=http://sanitizer:8002/api/sanitize`
- **Payload**: 
  ```json
  {
    "input_type": "task|qna|info|image|fixlog|solution_entry",
    "payload": { ... }
  }
  ```

### 2. Sanitizer → Whis
- **Endpoint**: `POST /api/sanitize`
- **Environment Variable**: `WHIS_URL=http://whis:8003/api/whis/train`
- **Payload**: 
  ```json
  {
    "input_type": "task|qna|info|image|fixlog|solution_entry",
    "payload": { ... }
  }
  ```

### 3. Whis Training + Rune/Orb Generation
- **Endpoint**: `POST /api/whis/train`
- **Response (Match Found)**: 
  ```json
  {
    "status": "match_found",
    "type": "task",
    "category": "katie|audit|igris|whis|links",
    "orb_id": "orb-12345678",
    "rune_id": "rune-12345678",
    "autonomous": true,
    "message": "Existing pattern matched, ready for deployment"
  }
  ```
- **Response (No Match)**: 
  ```json
  {
    "status": "no_match",
    "type": "task",
    "category": "katie|audit|igris|whis|links",
    "reason": "New task pattern",
    "needs_approval": true,
    "message": "New pattern detected, requires manual review"
  }
  ```
- **Response (Solution Entry)**: 
  ```json
  {
    "status": "rune_created",
    "type": "solution_entry",
    "category": "katie|audit|igris|whis|links",
    "rune_id": "rune-123456",
    "task_id": "cka-netfix",
    "solution_steps": 4,
    "result": "Success",
    "message": "Solution rune created and auto-trained: rune-123456"
  }
  ```

### 4. FickNury Evaluation + Deployment
- **Endpoint**: `POST /api/ficknury/evaluate`
- **Payload**:
  ```json
  {
    "task_id": "task-uuid",
    "task_description": "Create storageclass for fast SSD",
    "agent": "katie",
    "approved": false
  }
  ```
- **Response (Awaiting Approval)**:
  ```json
  {
    "status": "awaiting_approval",
    "agent": "katie",
    "task_id": "task-uuid",
    "score": 0.95,
    "message": "Task approved for automation, awaiting deployment approval"
  }
  ```
- **Response (Deployed)**:
  ```json
  {
    "status": "deployed",
    "agent": "katie",
    "task_id": "task-uuid",
    "score": 0.95,
    "message": "Successfully deployed katie for task task-uuid"
  }
  ```

## Solution Entry Pipeline

### Special Handling for Solution Entries
- **Auto-Detection**: Data collector recognizes `solution_entry` type
- **Enhanced Sanitization**: Special cleaning for solution paths and sensitive data
- **Auto-Training**: Whis immediately creates runes without approval workflow
- **Rune Creation**: Automatic rune generation for verified solutions

### Solution Entry Payload Example
```json
{
  "input_type": "solution_entry",
  "payload": {
    "task_id": "cka-netfix",
    "task_description": "Fixed CoreDNS crash due to bad ConfigMap",
    "solution_path": [
      "kubectl logs coredns...",
      "found bad forward . 8.8.8.8 line",
      "corrected ConfigMap",
      "rolled coredns daemonset"
    ],
    "result": "Success"
  }
}
```

## Legacy Support

### Kafka Integration (Backward Compatibility)
- **Task Collection**: `POST /api/collect/task` → Kafka topic `raw-tasks`
- **QnA Collection**: `POST /api/collect/qna` → Kafka topic `raw-qna`
- **Info Collection**: `POST /api/collect/info` → Kafka topic `raw-info`

### Legacy Endpoints
- **Whis**: `POST /api/whis/train-nightly` (batch processing)
- **FickNury**: `POST /api/ficknury/evaluate-task` (simple evaluation)

## Error Handling

### Data Collector
- Returns `sent_to_sanitizer: false` if sanitizer is unavailable
- Includes error details in response
- Special handling for solution entries

### Sanitizer
- Returns `forwarded_to_whis: false` if whis is unavailable
- Includes error details in response
- Still saves sanitized data locally
- Enhanced sanitization for solution paths

### Whis
- Returns error status if processing fails
- Logs detailed error information
- Handles both match and no-match scenarios
- Auto-training for solution entries

### FickNury
- Returns deployment failure status if deployment fails
- Handles approval workflow
- Provides detailed scoring and status information

## Testing

### Run Complete Flow Test
```bash
python test_data_collector_sanitizer_whis_flow.py
```

### Run Solution Entry Test
```bash
python test_solution_entry_pipeline.py
```

### Run Whis → FickNury Flow Test
```bash
python test_whis_ficknury_integration.py
```

### Run Individual Service Tests
```bash
python test_sanitizer_whis_communication.py
```

### Test Solution Entry with Curl
```bash
curl -X POST http://localhost:8001/api/collect \
  -H "Content-Type: application/json" \
  -d '{
        "input_type": "solution_entry",
        "payload": {
            "task_id": "cka-netfix",
            "task_description": "Fixed CoreDNS crash due to bad ConfigMap",
            "solution_path": [
              "kubectl logs coredns...",
              "found bad forward . 8.8.8.8 line",
              "corrected ConfigMap",
              "rolled coredns daemonset"
            ],
            "result": "Success"
        }
      }'
```

## Environment Variables

### Required for Service Communication
```bash
# Data Collector → Sanitizer
SANITIZER_URL=http://sanitizer:8002/api/sanitize

# Sanitizer → Whis
WHIS_URL=http://whis:8003/api/whis/train
```

### Docker Compose Configuration
```yaml
data-collector:
  environment:
    - SANITIZER_URL=http://sanitizer:8002/api/sanitize

sanitizer:
  environment:
    - WHIS_URL=http://whis:8003/api/whis/train
```

## Benefits

1. **Direct Communication**: Services communicate directly via HTTP
2. **Real-time Processing**: No delays from message queue processing
3. **Intelligent Routing**: Whis determines task category and automation potential
4. **Approval Workflow**: FickNury handles approval and deployment logic
5. **Solution Auto-Training**: Verified solutions automatically create runes
6. **Enhanced Sanitization**: Special handling for solution paths and sensitive data
7. **Error Handling**: Immediate feedback on communication failures
8. **Backward Compatibility**: Legacy Kafka endpoints still work
9. **Flexible Routing**: Easy to modify communication paths
10. **Monitoring**: Clear visibility into data flow and failures
11. **Automation Scoring**: FickNury evaluates automation feasibility
12. **Agent Deployment**: Automatic deployment of appropriate agents 