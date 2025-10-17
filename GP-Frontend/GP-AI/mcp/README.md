# MCP (Model Context Protocol) - External API Integration Layer

**Status:** 🚧 **PLANNED FOR FUTURE** 🚧
**Purpose:** Enable Jade to interact with external APIs and services
**Current:** Basic structure exists, full implementation pending

---

## 🎯 Intended Purpose

The MCP layer will allow Jade (our AI security assistant) to interact with external services:

### Planned External Integrations
- **Gmail API** - Send security reports via email
- **AWS SDK** - Perform cloud security operations
- **GitHub API** - Create PRs, manage repositories
- **Slack API** - Send notifications to teams
- **Web Scraping** - Gather threat intelligence
- **Other Cloud Providers** - Azure, GCP integrations

---

## 📁 Current Structure

```
mcp/
├── README.md                           # This file
├── server.py                           # Basic MCP server (9.7KB)
├── agents/                             # ⚠️ Legacy - may be refactored
│   ├── client_intelligence_agent.py
│   ├── consulting_remediation_agent.py
│   └── implementation_planning_agent.py
└── config/
    └── mcp_config.yaml                 # MCP configuration
```

---

## ⚠️ Current Status

### What Exists
- ✅ `server.py` - Basic MCP server implementation
- ✅ `mcp_config.yaml` - Configuration file
- ✅ `agents/` directory with 3 agent files (3095 lines)

### What's Pending
- 🚧 External API connectors (Gmail, AWS, GitHub, etc.)
- 🚧 Authentication/credential management for external services
- 🚧 Rate limiting and retry logic
- 🚧 Error handling for external service failures
- 🚧 Integration with Jade orchestrator

### Note on agents/ Directory
The current `agents/` files may be refactored as they appear to contain:
- Business logic that might belong in core/
- Agent patterns that might be better as tools/
- Planning to evaluate purpose and restructure

---

## 🔮 Future Architecture (Planned)

### External API Connectors
```
mcp/
├── server.py                    # MCP server
├── connectors/                  # External API integrations
│   ├── gmail_connector.py
│   ├── aws_connector.py
│   ├── github_connector.py
│   ├── slack_connector.py
│   └── webscraper_connector.py
├── middleware/                  # Auth, rate limiting, retry
│   ├── auth_handler.py
│   ├── rate_limiter.py
│   └── retry_logic.py
└── config/
    └── mcp_config.yaml
```

---

## 🚀 How It Will Work (Future)

### Example: Send Security Report via Gmail
```python
# Jade orchestrator calls MCP
from mcp.connectors.gmail_connector import GmailConnector

gmail = GmailConnector()
gmail.send_email(
    to="security@company.com",
    subject="Security Scan Results",
    body=report_content,
    attachments=[scan_results_pdf]
)
```

### Example: Create GitHub PR with Fixes
```python
# Jade orchestrator calls MCP
from mcp.connectors.github_connector import GitHubConnector

github = GitHubConnector()
github.create_pull_request(
    repo="company/project",
    title="Security fixes from Jade",
    branch="jade-security-fixes",
    files=fixed_files
)
```

---

## 📝 Integration with Jade

### Jade Architecture
```
┌─────────────────────────────────────────┐
│  Jade (jade_orchestrator.py)           │
│  - Main AI brain                        │
│  - Understands user requests            │
│  - Coordinates agents and MCP           │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐      ┌────────────┐
│ Agents  │      │    MCP     │
│ (Tools) │      │ (External) │
└─────────┘      └────────────┘
│                │
• policy_agent   • Gmail
• troubleshoot   • AWS
• scanner        • GitHub
• fixer          • Slack
```

### When Jade Uses MCP
- **Sending reports** - Use Gmail connector
- **Cloud operations** - Use AWS/Azure/GCP connectors
- **Creating PRs** - Use GitHub connector
- **Notifications** - Use Slack connector
- **Threat intel** - Use web scraping

---

## 🔧 Development Roadmap

### Phase 1: Core Connectors (Future)
- [ ] Gmail connector
- [ ] AWS SDK wrapper
- [ ] GitHub API integration
- [ ] Basic authentication

### Phase 2: Advanced Features (Future)
- [ ] Slack notifications
- [ ] Web scraping for threat intel
- [ ] Rate limiting
- [ ] Retry logic
- [ ] Error handling

### Phase 3: Multi-Client Support (Future)
- [ ] Tenant isolation
- [ ] Per-client credentials
- [ ] Usage tracking
- [ ] Billing integration

---

## 📚 References

- **Model Context Protocol Spec:** https://modelcontextprotocol.io/
- **Jade Orchestrator:** `GP-AI/agents/jade_orchestrator.py`
- **Platform Config:** `GP-AI/config/platform_config.py`

---

## 🤝 Contributing

When implementing MCP connectors:

1. **Follow pattern:** Each external service gets a connector class
2. **Use secrets manager:** Never hardcode credentials
3. **Implement retries:** External APIs fail, handle gracefully
4. **Add tests:** Test with mocked external services
5. **Document:** Update this README with new connectors

---

**Status:** Placeholder for future external API integration layer
**Last Updated:** 2025-10-16
**Next Steps:** Implement core connectors (Gmail, AWS, GitHub) when external integration is prioritized
