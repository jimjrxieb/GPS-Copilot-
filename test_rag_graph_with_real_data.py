#!/usr/bin/env python3
"""
Test RAG Graph with real scan data (1658 findings!)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from GP_AI.core.rag_graph_engine import security_graph

print("=" * 80)
print("Testing RAG Graph with Real Scan Data")
print("=" * 80)

# Get current stats
stats = security_graph.get_stats()
print(f"\n📊 Current Graph State:")
print(f"   Total nodes: {stats['total_nodes']}")
print(f"   Total edges: {stats['total_edges']}")
print(f"   Findings: {stats['node_types']['finding']}")
print(f"   Projects: {stats['node_types']['project']}")
print(f"   CWEs: {stats['node_types']['cwe']}")
print(f"   OWASP: {stats['node_types']['owasp']}")

# Test 1: Find all SQL injection findings
print("\n\n🧪 Test 1: Find all SQL injection findings")
sql_findings = []
for node_id in security_graph.graph.nodes():
    node_data = security_graph.graph.nodes[node_id]
    if node_data.get("node_type") == "finding":
        desc = node_data.get("description", "").lower()
        if "sql" in desc or "injection" in desc:
            sql_findings.append((node_id, node_data))

print(f"✅ Found {len(sql_findings)} SQL injection findings")
for finding_id, data in sql_findings[:5]:
    print(f"   - {finding_id}")
    print(f"     File: {data.get('file_path', 'N/A')}")
    print(f"     Line: {data.get('line_number', 'N/A')}")
    print(f"     Severity: {data.get('severity', 'N/A')}")

# Test 2: Multi-hop query: CWE-78 → related findings
print("\n\n🧪 Test 2: Multi-hop query from CWE-78 (OS Command Injection)")
if "CWE-78" in security_graph.graph:
    path, nodes = security_graph.traverse(
        "CWE-78",
        max_depth=2,
        edge_types=["instance_of"]  # Only traverse instance_of edges (reverse direction)
    )

    # Find findings that reference CWE-78
    cwe_78_findings = []
    for node_id in security_graph.graph.nodes():
        node_data = security_graph.graph.nodes[node_id]
        if node_data.get("node_type") == "finding":
            # Check if this finding links to CWE-78
            neighbors = security_graph.get_neighbors(node_id, edge_type="instance_of")
            if "CWE-78" in neighbors:
                cwe_78_findings.append((node_id, node_data))

    print(f"✅ Found {len(cwe_78_findings)} findings related to CWE-78")
    for finding_id, data in cwe_78_findings[:5]:
        print(f"   - {finding_id}")
        print(f"     Scanner: {data.get('scanner', 'N/A')}")
        print(f"     File: {data.get('file_path', 'N/A')}")
        print(f"     Severity: {data.get('severity', 'N/A')}")
else:
    print("⚠️  CWE-78 not in graph")

# Test 3: Project-level analysis
print("\n\n🧪 Test 3: Project-level finding analysis")
projects = [node_id for node_id in security_graph.graph.nodes()
            if security_graph.graph.nodes[node_id].get("node_type") == "project"]

for project_id in projects:
    # Find all findings for this project
    project_findings = []
    for node_id in security_graph.graph.nodes():
        node_data = security_graph.graph.nodes[node_id]
        if node_data.get("node_type") == "finding":
            # Check if finding links to this project
            neighbors = security_graph.get_neighbors(node_id, edge_type="found_in")
            if project_id in neighbors:
                project_findings.append(node_data)

    # Count by severity
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
    for finding in project_findings:
        sev = finding.get("severity", "UNKNOWN").upper()
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    print(f"\n   {project_id}:")
    print(f"     Total findings: {len(project_findings)}")
    print(f"     Severity breakdown:")
    for sev, count in severity_counts.items():
        if count > 0:
            print(f"       {sev}: {count}")

# Test 4: Cross-project similar findings
print("\n\n🧪 Test 4: Cross-project analysis (same CWE in multiple projects)")
cwe_project_map = {}

for node_id in security_graph.graph.nodes():
    node_data = security_graph.graph.nodes[node_id]
    if node_data.get("node_type") == "finding":
        # Get CWE for this finding
        cwe_neighbors = security_graph.get_neighbors(node_id, edge_type="instance_of")
        project_neighbors = security_graph.get_neighbors(node_id, edge_type="found_in")

        for cwe in cwe_neighbors:
            if cwe not in cwe_project_map:
                cwe_project_map[cwe] = set()
            cwe_project_map[cwe].update(project_neighbors)

# Find CWEs that appear in multiple projects
multi_project_cwes = {cwe: projects for cwe, projects in cwe_project_map.items() if len(projects) > 1}

print(f"✅ Found {len(multi_project_cwes)} CWEs appearing in multiple projects:")
for cwe, projects in list(multi_project_cwes.items())[:5]:
    cwe_data = security_graph.graph.nodes.get(cwe, {})
    print(f"   - {cwe}: {cwe_data.get('name', 'N/A')}")
    print(f"     Projects: {list(projects)}")

# Test 5: High-severity findings near OWASP categories
print("\n\n🧪 Test 5: OWASP category → CWE → HIGH severity findings")

owasp_high_severity = {}

for owasp_id in security_graph.graph.nodes():
    if not owasp_id.startswith("OWASP:"):
        continue

    # Get CWEs categorized under this OWASP
    owasp_data = security_graph.graph.nodes[owasp_id]

    # Find CWEs that link to this OWASP
    related_cwes = []
    for node_id in security_graph.graph.nodes():
        node_data = security_graph.graph.nodes[node_id]
        if node_data.get("node_type") == "cwe":
            # Check if this CWE links to OWASP
            neighbors = security_graph.get_neighbors(node_id, edge_type="categorized_as")
            if owasp_id in neighbors:
                related_cwes.append(node_id)

    # For each CWE, count HIGH severity findings
    high_count = 0
    for cwe in related_cwes:
        for node_id in security_graph.graph.nodes():
            node_data = security_graph.graph.nodes[node_id]
            if node_data.get("node_type") == "finding" and node_data.get("severity") == "HIGH":
                neighbors = security_graph.get_neighbors(node_id, edge_type="instance_of")
                if cwe in neighbors:
                    high_count += 1

    if high_count > 0:
        owasp_high_severity[owasp_id] = {
            "name": owasp_data.get("name"),
            "high_findings": high_count,
            "related_cwes": related_cwes
        }

print(f"✅ OWASP categories with HIGH severity findings:")
for owasp_id, data in sorted(owasp_high_severity.items(), key=lambda x: x[1]['high_findings'], reverse=True)[:5]:
    print(f"   - {owasp_id}: {data['name']}")
    print(f"     HIGH findings: {data['high_findings']}")
    print(f"     Related CWEs: {data['related_cwes']}")

print("\n" + "=" * 80)
print("RAG Graph with Real Data Test Complete!")
print("=" * 80)

print("\n🎯 What this demonstrates:")
print("1. ✅ Multi-hop reasoning (CWE → Findings → Projects)")
print("2. ✅ Cross-project analysis (same issue in multiple codebases)")
print("3. ✅ Severity-based filtering")
print("4. ✅ OWASP category mapping")
print("5. ✅ Project-level security posture assessment")

print("\n💡 This enables:")
print("- 'Show me all HIGH severity SQL injection findings across all projects'")
print("- 'Which OWASP categories are most violated in my codebase?'")
print("- 'Are there patterns of the same CWE appearing in multiple projects?'")
print("- 'What's the security posture of project X vs project Y?'")