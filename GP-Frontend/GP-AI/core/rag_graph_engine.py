"""
RAG Graph Engine - Knowledge Graph for Security Intelligence

Combines NetworkX graph structure with vector embeddings for multi-hop reasoning.
Enables contextual security analysis by traversing relationships between:
- CVEs (vulnerabilities)
- CWEs (weakness types)
- OWASP categories
- Scan findings
- Remediation patterns
- Compliance frameworks

This is the "intelligence layer" that makes Jade a smart consultant, not just a search tool.
"""

import networkx as nx
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple, Optional
from datetime import datetime
import hashlib

# Import the existing RAG engine for vector embeddings
# Note: This is optional, graph can work standalone
try:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from rag_engine import rag_engine
except ImportError:
    print("⚠️  RAG Engine not found, running in standalone mode")
    rag_engine = None


class SecurityKnowledgeGraph:
    """
    Multi-hop knowledge graph for security intelligence.

    Architecture:
    - NetworkX MultiDiGraph for relationships
    - Node types: CVE, CWE, OWASP, Finding, Policy, Fix, Tool, Project
    - Edge types: maps_to, categorized_as, instance_of, detected_by, fixed_by, similar_to, violates
    """

    def __init__(self, graph_path: Optional[Path] = None):
        """Initialize security knowledge graph"""

        # Initialize graph (MultiDiGraph allows multiple edges between nodes)
        self.graph = nx.MultiDiGraph()

        # Track node types for efficient filtering
        self.node_types = {
            "cve": set(),
            "cwe": set(),
            "owasp": set(),
            "finding": set(),
            "policy": set(),
            "fix": set(),
            "tool": set(),
            "project": set()
        }

        # Graph persistence path
        if graph_path:
            self.graph_path = Path(graph_path)
        else:
            # Default: GP-DATA/knowledge-base/security_graph.pkl at GP-copilot root
            gp_copilot_root = Path(__file__).parent.parent.parent.parent  # GP-Frontend/GP-AI/core -> GP-copilot
            self.graph_path = gp_copilot_root / "GP-DATA" / "knowledge-base" / "security_graph.pkl"

        self.graph_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing graph or build new one
        if self.graph_path.exists():
            self.load_graph()
        else:
            self.build_base_knowledge_graph()

    # ========== GRAPH BUILDING ==========

    def build_base_knowledge_graph(self):
        """Build initial security knowledge graph with OWASP, CWE, common patterns"""

        print("🏗️  Building base security knowledge graph...")

        # === OWASP Top 10 2021 Nodes ===
        owasp_categories = [
            {
                "id": "OWASP:A01:2021",
                "name": "Broken Access Control",
                "description": "Restrictions on what authenticated users are allowed to do are often not properly enforced"
            },
            {
                "id": "OWASP:A02:2021",
                "name": "Cryptographic Failures",
                "description": "Failures related to cryptography which often leads to sensitive data exposure"
            },
            {
                "id": "OWASP:A03:2021",
                "name": "Injection",
                "description": "SQL, NoSQL, OS command, LDAP injection vulnerabilities"
            },
            {
                "id": "OWASP:A04:2021",
                "name": "Insecure Design",
                "description": "Missing or ineffective control design"
            },
            {
                "id": "OWASP:A05:2021",
                "name": "Security Misconfiguration",
                "description": "Missing security hardening, improper configurations"
            },
            {
                "id": "OWASP:A06:2021",
                "name": "Vulnerable and Outdated Components",
                "description": "Using components with known vulnerabilities"
            },
            {
                "id": "OWASP:A07:2021",
                "name": "Identification and Authentication Failures",
                "description": "Authentication and session management failures"
            },
            {
                "id": "OWASP:A08:2021",
                "name": "Software and Data Integrity Failures",
                "description": "Insecure CI/CD, unverified updates"
            },
            {
                "id": "OWASP:A09:2021",
                "name": "Security Logging and Monitoring Failures",
                "description": "Insufficient logging and monitoring"
            },
            {
                "id": "OWASP:A10:2021",
                "name": "Server-Side Request Forgery",
                "description": "SSRF flaws occur when a web app fetches a remote resource without validating the user-supplied URL"
            }
        ]

        for owasp in owasp_categories:
            self.add_node(
                node_id=owasp["id"],
                node_type="owasp",
                name=owasp["name"],
                description=owasp["description"],
                severity="high"
            )

        # === Common CWE Nodes ===
        cwe_mappings = [
            # Injection-related CWEs → OWASP A03
            {"id": "CWE-89", "name": "SQL Injection", "owasp": "OWASP:A03:2021"},
            {"id": "CWE-79", "name": "Cross-site Scripting (XSS)", "owasp": "OWASP:A03:2021"},
            {"id": "CWE-78", "name": "OS Command Injection", "owasp": "OWASP:A03:2021"},
            {"id": "CWE-90", "name": "LDAP Injection", "owasp": "OWASP:A03:2021"},

            # Access Control → OWASP A01
            {"id": "CWE-284", "name": "Improper Access Control", "owasp": "OWASP:A01:2021"},
            {"id": "CWE-285", "name": "Improper Authorization", "owasp": "OWASP:A01:2021"},
            {"id": "CWE-862", "name": "Missing Authorization", "owasp": "OWASP:A01:2021"},

            # Crypto failures → OWASP A02
            {"id": "CWE-327", "name": "Use of Broken Crypto Algorithm", "owasp": "OWASP:A02:2021"},
            {"id": "CWE-326", "name": "Inadequate Encryption Strength", "owasp": "OWASP:A02:2021"},
            {"id": "CWE-311", "name": "Missing Encryption of Sensitive Data", "owasp": "OWASP:A02:2021"},

            # Misconfiguration → OWASP A05
            {"id": "CWE-16", "name": "Configuration", "owasp": "OWASP:A05:2021"},
            {"id": "CWE-269", "name": "Improper Privilege Management", "owasp": "OWASP:A05:2021"},

            # Vulnerable components → OWASP A06
            {"id": "CWE-1104", "name": "Use of Unmaintained Third Party Components", "owasp": "OWASP:A06:2021"},

            # Auth failures → OWASP A07
            {"id": "CWE-287", "name": "Improper Authentication", "owasp": "OWASP:A07:2021"},
            {"id": "CWE-521", "name": "Weak Password Requirements", "owasp": "OWASP:A07:2021"},
        ]

        for cwe in cwe_mappings:
            # Add CWE node
            self.add_node(
                node_id=cwe["id"],
                node_type="cwe",
                name=cwe["name"],
                description=f"Common Weakness Enumeration: {cwe['name']}"
            )

            # Link CWE → OWASP
            self.add_edge(
                source=cwe["id"],
                target=cwe["owasp"],
                edge_type="categorized_as",
                relationship="CWE categorized under OWASP category"
            )

        # === Security Tools ===
        tools = [
            {"id": "tool:trivy", "name": "Trivy", "type": "container_scanner"},
            {"id": "tool:bandit", "name": "Bandit", "type": "python_sast"},
            {"id": "tool:semgrep", "name": "Semgrep", "type": "sast"},
            {"id": "tool:checkov", "name": "Checkov", "type": "iac_scanner"},
            {"id": "tool:gitleaks", "name": "Gitleaks", "type": "secret_scanner"},
            {"id": "tool:kics", "name": "KICS", "type": "iac_scanner"},
        ]

        for tool in tools:
            self.add_node(
                node_id=tool["id"],
                node_type="tool",
                name=tool["name"],
                scanner_type=tool["type"]
            )

        # === Common Kubernetes Security Patterns ===
        k8s_patterns = [
            {
                "id": "fix:k8s-privileged-false",
                "name": "Disable Privileged Containers",
                "fix": "Set securityContext.privileged: false",
                "cwe": "CWE-250"
            },
            {
                "id": "fix:k8s-run-as-nonroot",
                "name": "Run as Non-Root User",
                "fix": "Set securityContext.runAsNonRoot: true",
                "cwe": "CWE-250"
            },
            {
                "id": "fix:k8s-network-policy",
                "name": "Implement Network Policies",
                "fix": "Create NetworkPolicy with default deny",
                "cwe": "CWE-284"
            }
        ]

        for pattern in k8s_patterns:
            self.add_node(
                node_id=pattern["id"],
                node_type="fix",
                name=pattern["name"],
                fix_content=pattern["fix"]
            )

            # Link fix → CWE it addresses
            if pattern.get("cwe"):
                self.add_edge(
                    source=pattern["id"],
                    target=pattern["cwe"],
                    edge_type="remediates",
                    relationship="Fix remediates this weakness"
                )

        print(f"✅ Built base knowledge graph: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")

        # Save graph
        self.save_graph()

    def add_node(self, node_id: str, node_type: str, **attributes):
        """Add node to graph with type tracking"""

        # Add node with attributes
        self.graph.add_node(
            node_id,
            node_type=node_type,
            created_at=datetime.now().isoformat(),
            **attributes
        )

        # Track node type
        if node_type in self.node_types:
            self.node_types[node_type].add(node_id)

    def add_edge(self, source: str, target: str, edge_type: str, **attributes):
        """Add edge to graph"""

        self.graph.add_edge(
            source,
            target,
            edge_type=edge_type,
            created_at=datetime.now().isoformat(),
            **attributes
        )

    # ========== GRAPH TRAVERSAL ==========

    def traverse(
        self,
        start_node: str,
        max_depth: int = 2,
        edge_types: Optional[List[str]] = None,
        node_types: Optional[List[str]] = None
    ) -> Tuple[List[str], List[Dict]]:
        """
        Multi-hop graph traversal from starting node.

        Returns:
            - path: List of node IDs in traversal order
            - nodes: List of node data dictionaries
        """

        if start_node not in self.graph:
            return [], []

        visited = set()
        path = []
        nodes = []

        def _traverse_recursive(node_id: str, depth: int):
            if depth > max_depth or node_id in visited:
                return

            visited.add(node_id)
            path.append(node_id)

            # Get node data
            node_data = dict(self.graph.nodes[node_id])
            node_data["id"] = node_id
            nodes.append(node_data)

            # Traverse outgoing edges
            for _, neighbor, edge_data in self.graph.out_edges(node_id, data=True):
                # Filter by edge type if specified
                if edge_types and edge_data.get("edge_type") not in edge_types:
                    continue

                # Filter by node type if specified
                if node_types:
                    neighbor_type = self.graph.nodes[neighbor].get("node_type")
                    if neighbor_type not in node_types:
                        continue

                _traverse_recursive(neighbor, depth + 1)

        _traverse_recursive(start_node, 0)

        return path, nodes

    def find_nodes_by_query(self, query: str, node_type: Optional[str] = None) -> List[str]:
        """
        Find nodes matching query string.
        Searches node IDs, names, and descriptions.
        """

        query_lower = query.lower()
        matching_nodes = []

        for node_id, node_data in self.graph.nodes(data=True):
            # Filter by node type if specified
            if node_type and node_data.get("node_type") != node_type:
                continue

            # Search in node ID
            if query_lower in node_id.lower():
                matching_nodes.append(node_id)
                continue

            # Search in node name
            if "name" in node_data and query_lower in node_data["name"].lower():
                matching_nodes.append(node_id)
                continue

            # Search in node description
            if "description" in node_data and query_lower in node_data["description"].lower():
                matching_nodes.append(node_id)
                continue

        return matching_nodes

    def find_path(self, source: str, target: str) -> Optional[List[str]]:
        """Find shortest path between two nodes"""

        try:
            return nx.shortest_path(self.graph, source, target)
        except nx.NetworkXNoPath:
            return None

    def get_neighbors(self, node_id: str, edge_type: Optional[str] = None) -> List[str]:
        """Get immediate neighbors of a node, optionally filtered by edge type"""

        if node_id not in self.graph:
            return []

        neighbors = []
        for _, neighbor, edge_data in self.graph.out_edges(node_id, data=True):
            if edge_type is None or edge_data.get("edge_type") == edge_type:
                neighbors.append(neighbor)

        return neighbors

    def get_related_findings(self, cve_id: str) -> List[Dict]:
        """
        Get all findings related to a CVE.
        Traverses: CVE → CWE → Findings
        """

        # Find CWE nodes linked to CVE
        cwes = self.get_neighbors(cve_id, edge_type="maps_to")

        # Find findings that are instances of these CWEs
        related_findings = []
        for cwe in cwes:
            # Get all findings that are instances of this CWE
            for node_id in self.graph.nodes():
                node_data = self.graph.nodes[node_id]
                if node_data.get("node_type") == "finding":
                    # Check if finding links to this CWE
                    if cwe in self.get_neighbors(node_id, edge_type="instance_of"):
                        finding_data = dict(node_data)
                        finding_data["id"] = node_id
                        related_findings.append(finding_data)

        return related_findings

    # ========== SCAN FINDING INTEGRATION ==========

    def add_finding_from_scan(
        self,
        finding_id: str,
        scanner: str,
        severity: str,
        cwe_id: Optional[str] = None,
        cve_id: Optional[str] = None,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        description: Optional[str] = None,
        project_id: Optional[str] = None
    ):
        """
        Add a finding from security scan to knowledge graph.
        Creates nodes and relationships automatically.
        """

        # Add finding node
        self.add_node(
            node_id=finding_id,
            node_type="finding",
            scanner=scanner,
            severity=severity,
            file_path=file_path,
            line_number=line_number,
            description=description
        )

        # Link to scanner tool
        tool_id = f"tool:{scanner.lower()}"
        if tool_id in self.graph:
            self.add_edge(
                source=finding_id,
                target=tool_id,
                edge_type="detected_by",
                relationship="Finding detected by tool"
            )

        # Link to CWE if provided
        if cwe_id and cwe_id in self.graph:
            self.add_edge(
                source=finding_id,
                target=cwe_id,
                edge_type="instance_of",
                relationship="Finding is instance of CWE"
            )

        # Link to CVE if provided
        if cve_id:
            # Add CVE node if not exists
            if cve_id not in self.graph:
                self.add_node(
                    node_id=cve_id,
                    node_type="cve",
                    name=cve_id
                )

            self.add_edge(
                source=finding_id,
                target=cve_id,
                edge_type="relates_to",
                relationship="Finding relates to CVE"
            )

        # Link to project if provided
        if project_id:
            # Add project node if not exists
            if project_id not in self.graph:
                self.add_node(
                    node_id=project_id,
                    node_type="project",
                    name=project_id
                )

            self.add_edge(
                source=finding_id,
                target=project_id,
                edge_type="found_in",
                relationship="Finding found in project"
            )

    # ========== PERSISTENCE ==========

    def save_graph(self):
        """Save graph to disk"""

        try:
            with open(self.graph_path, 'wb') as f:
                pickle.dump({
                    'graph': self.graph,
                    'node_types': self.node_types
                }, f)

            print(f"💾 Saved knowledge graph to {self.graph_path}")
        except Exception as e:
            print(f"❌ Error saving graph: {e}")

    def load_graph(self):
        """Load graph from disk"""

        try:
            with open(self.graph_path, 'rb') as f:
                data = pickle.load(f)
                self.graph = data['graph']
                self.node_types = data['node_types']

            print(f"📦 Loaded knowledge graph: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        except Exception as e:
            print(f"❌ Error loading graph: {e}")
            print("🏗️  Building new graph...")
            self.build_base_knowledge_graph()

    # ========== STATS & EXPORT ==========

    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""

        stats = {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_types": {
                node_type: len(nodes)
                for node_type, nodes in self.node_types.items()
            },
            "edge_types": {}
        }

        # Count edge types
        for _, _, edge_data in self.graph.edges(data=True):
            edge_type = edge_data.get("edge_type", "unknown")
            stats["edge_types"][edge_type] = stats["edge_types"].get(edge_type, 0) + 1

        return stats

    def export_to_json(self, output_path: Path):
        """Export graph to JSON for visualization"""

        # Convert graph to JSON-serializable format
        data = {
            "nodes": [
                {"id": node_id, **node_data}
                for node_id, node_data in self.graph.nodes(data=True)
            ],
            "edges": [
                {
                    "source": source,
                    "target": target,
                    **edge_data
                }
                for source, target, edge_data in self.graph.edges(data=True)
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        print(f"📤 Exported graph to {output_path}")


# Global graph engine instance
security_graph = SecurityKnowledgeGraph()


if __name__ == "__main__":
    print("=" * 80)
    print("Security Knowledge Graph - Test")
    print("=" * 80)

    # Test basic graph operations
    print("\n📊 Graph Statistics:")
    stats = security_graph.get_stats()
    print(f"Nodes: {stats['total_nodes']}")
    print(f"Edges: {stats['total_edges']}")
    print(f"\nNode Types:")
    for node_type, count in stats['node_types'].items():
        print(f"  {node_type}: {count}")
    print(f"\nEdge Types:")
    for edge_type, count in stats['edge_types'].items():
        print(f"  {edge_type}: {count}")

    # Test query
    print("\n\n🔍 Test Query: 'injection'")
    matches = security_graph.find_nodes_by_query("injection")
    print(f"Found {len(matches)} nodes:")
    for node_id in matches[:5]:
        node_data = security_graph.graph.nodes[node_id]
        print(f"  - {node_id}: {node_data.get('name', 'N/A')}")

    # Test traversal
    print("\n\n🚶 Test Traversal: From CWE-89 (SQL Injection)")
    if "CWE-89" in security_graph.graph:
        path, nodes = security_graph.traverse("CWE-89", max_depth=2)
        print(f"Traversed {len(nodes)} nodes:")
        for node in nodes:
            print(f"  {node['id']} ({node['node_type']}): {node.get('name', 'N/A')}")

    # Test adding a finding
    print("\n\n➕ Test: Adding scan finding")
    security_graph.add_finding_from_scan(
        finding_id="finding:test-001",
        scanner="bandit",
        severity="HIGH",
        cwe_id="CWE-89",
        file_path="app.py",
        line_number=42,
        description="SQL injection vulnerability detected",
        project_id="project:test-app"
    )

    # Show updated stats
    stats = security_graph.get_stats()
    print(f"Updated nodes: {stats['total_nodes']}")
    print(f"Updated edges: {stats['total_edges']}")

    print("\n✅ Graph engine test complete!")