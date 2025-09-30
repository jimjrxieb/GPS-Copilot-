#!/usr/bin/env python3
"""
Agent Metadata and Tagging System for GP-DATA
Standardized metadata format for all agent operations
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

class AgentMetadata:
    """
    Standardized metadata format for all GP-Copilot agent operations.

    Ensures consistent tagging, tracking, and auditability across all agents.
    """

    VALID_AGENTS = {
        "cka_agent": {
            "name": "CKA Kubernetes Agent",
            "domain": "kubernetes_security",
            "output_dir": "analysis"
        },
        "iac_agent": {
            "name": "Infrastructure as Code Agent",
            "domain": "infrastructure_security",
            "output_dir": "fixes"
        },
        "secrets_agent": {
            "name": "Secrets Management Agent",
            "domain": "secrets_management",
            "output_dir": "analysis"
        },
        "devsecops_agent": {
            "name": "DevSecOps CI/CD Agent",
            "domain": "cicd_security",
            "output_dir": "workflows"
        },
        "research_agent": {
            "name": "Research & Documentation Agent",
            "domain": "security_research",
            "output_dir": "reports"
        },
        "qa_agent": {
            "name": "Quality Assurance Agent",
            "domain": "quality_assurance",
            "output_dir": "analysis"
        },
        "dfir_agent": {
            "name": "DFIR Support Agent",
            "domain": "threat_intelligence",
            "output_dir": "reports"
        },
        "client_support_agent": {
            "name": "Client Support Agent",
            "domain": "client_engagement",
            "output_dir": "deliverables"
        },
        "container_agent": {
            "name": "Container Security Agent",
            "domain": "container_security",
            "output_dir": "analysis"
        }
    }

    VALID_CONFIDENCE_LEVELS = ["high", "medium", "low"]

    VALID_DOMAINS = [
        "kubernetes_security",
        "infrastructure_security",
        "secrets_management",
        "cicd_security",
        "security_research",
        "quality_assurance",
        "threat_intelligence",
        "client_engagement",
        "container_security"
    ]

    def __init__(
        self,
        agent_id: str,
        operation: str,
        confidence: str,
        project_path: Optional[str] = None,
        client_name: Optional[str] = None,
        custom_tags: Optional[Dict[str, Any]] = None
    ):
        if agent_id not in self.VALID_AGENTS:
            raise ValueError(f"Invalid agent_id: {agent_id}. Must be one of {list(self.VALID_AGENTS.keys())}")

        if confidence not in self.VALID_CONFIDENCE_LEVELS:
            raise ValueError(f"Invalid confidence: {confidence}. Must be one of {self.VALID_CONFIDENCE_LEVELS}")

        self.agent_id = agent_id
        self.operation = operation
        self.confidence = confidence
        self.project_path = project_path
        self.client_name = client_name or "guidepoint"
        self.custom_tags = custom_tags or {}

        self.agent_info = self.VALID_AGENTS[agent_id]
        self.domain = self.agent_info["domain"]
        self.timestamp = datetime.now().isoformat()
        self.operation_id = self._generate_operation_id()

    def _generate_operation_id(self) -> str:
        """Generate unique operation ID"""
        timestamp_short = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        return f"{self.agent_id}_{self.operation}_{timestamp_short}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "operation_id": self.operation_id,
            "agent": {
                "id": self.agent_id,
                "name": self.agent_info["name"],
                "domain": self.domain
            },
            "operation": {
                "type": self.operation,
                "confidence": self.confidence,
                "timestamp": self.timestamp
            },
            "context": {
                "project_path": self.project_path,
                "client_name": self.client_name
            },
            "tags": {
                "domain": self.domain,
                "confidence": self.confidence,
                "agent_id": self.agent_id,
                **self.custom_tags
            }
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert metadata to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, output_dir: Path, result: Dict[str, Any]) -> Path:
        """
        Save operation with metadata to GP-DATA

        Args:
            output_dir: Directory to save operation
            result: Operation result data

        Returns:
            Path to saved file
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        operation_record = {
            "metadata": self.to_dict(),
            "result": result
        }

        filename = f"{self.operation_id}.json"
        output_file = output_dir / filename

        with open(output_file, 'w') as f:
            json.dump(operation_record, f, indent=2)

        return output_file

    @classmethod
    def get_agent_info(cls, agent_id: str) -> Dict[str, str]:
        """Get agent information by ID"""
        if agent_id not in cls.VALID_AGENTS:
            raise ValueError(f"Unknown agent: {agent_id}")
        return cls.VALID_AGENTS[agent_id]

    @classmethod
    def list_agents(cls) -> List[Dict[str, str]]:
        """List all registered agents"""
        return [
            {
                "id": agent_id,
                "name": info["name"],
                "domain": info["domain"],
                "output_dir": info["output_dir"]
            }
            for agent_id, info in cls.VALID_AGENTS.items()
        ]

    @classmethod
    def get_agents_by_domain(cls, domain: str) -> List[str]:
        """Get all agents for a specific domain"""
        return [
            agent_id for agent_id, info in cls.VALID_AGENTS.items()
            if info["domain"] == domain
        ]


class AgentAuditTrail:
    """
    Audit trail for agent operations.
    Tracks all agent executions for compliance and analysis.
    """

    def __init__(self, audit_file: Path):
        self.audit_file = audit_file
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.audit_file.exists():
            self._initialize_audit_file()

    def _initialize_audit_file(self):
        """Initialize audit trail file"""
        initial_data = {
            "created": datetime.now().isoformat(),
            "operations": []
        }
        with open(self.audit_file, 'w') as f:
            json.dump(initial_data, f, indent=2)

    def log_operation(self, metadata: AgentMetadata, result_summary: Dict[str, Any]):
        """Log agent operation to audit trail"""
        with open(self.audit_file, 'r') as f:
            audit_data = json.load(f)

        audit_entry = {
            "operation_id": metadata.operation_id,
            "timestamp": metadata.timestamp,
            "agent_id": metadata.agent_id,
            "operation": metadata.operation,
            "confidence": metadata.confidence,
            "client": metadata.client_name,
            "success": result_summary.get("success", False),
            "summary": result_summary
        }

        audit_data["operations"].append(audit_entry)

        with open(self.audit_file, 'w') as f:
            json.dump(audit_data, f, indent=2)

    def get_agent_history(self, agent_id: str, limit: int = 10) -> List[Dict]:
        """Get operation history for specific agent"""
        with open(self.audit_file, 'r') as f:
            audit_data = json.load(f)

        agent_ops = [
            op for op in audit_data["operations"]
            if op["agent_id"] == agent_id
        ]

        return sorted(agent_ops, key=lambda x: x["timestamp"], reverse=True)[:limit]

    def get_recent_operations(self, limit: int = 20) -> List[Dict]:
        """Get most recent operations across all agents"""
        with open(self.audit_file, 'r') as f:
            audit_data = json.load(f)

        return sorted(
            audit_data["operations"],
            key=lambda x: x["timestamp"],
            reverse=True
        )[:limit]


if __name__ == "__main__":
    print("🏷️  Agent Metadata & Tagging System")
    print()

    print("📋 Registered Agents:")
    for agent in AgentMetadata.list_agents():
        print(f"   {agent['id']:25} → {agent['name']:35} [{agent['domain']}] → {agent['output_dir']}/")

    print()
    print("🔍 Domains:")
    for domain in AgentMetadata.VALID_DOMAINS:
        agents = AgentMetadata.get_agents_by_domain(domain)
        print(f"   {domain:30} → {', '.join(agents)}")

    print()
    print("✅ Metadata system ready for agent integration")

    print()
    print("📝 Example Usage:")
    print("""
    from agent_metadata import AgentMetadata
    from gp_data_config import GPDataConfig

    # Create metadata
    metadata = AgentMetadata(
        agent_id="cka_agent",
        operation="assess_cluster",
        confidence="high",
        project_path="/path/to/project",
        client_name="TechCorp"
    )

    # Save operation with metadata
    config = GPDataConfig()
    result = {"findings": 5, "issues": 2}
    metadata.save(config.analysis, result)
    """)