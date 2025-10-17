#!/usr/bin/env python3
"""
Knowledge Graph Ingestion - Add JSONL Knowledge to Graph with Relationships
============================================================================

Takes knowledge from ChromaDB vectors and creates graph relationships:
- OPA policies → CIS benchmarks → Compliance frameworks
- Kubernetes concepts → RBAC violations → Fixes
- CKS exam questions → Real-world findings → Remediations

Usage:
    python graph_ingest_knowledge.py
    python graph_ingest_knowledge.py --dry-run
"""

import os
import sys
import json
import pickle
import argparse
import networkx as nx
from pathlib import Path
from typing import List, Dict, Any, Set
from datetime import datetime

# Force CPU mode
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "GP-Frontend" / "GP-AI"))
from core.rag_engine import RAGEngine


class KnowledgeGraphBuilder:
    """Builds knowledge graph from RAG vectors with semantic relationships"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.rag_engine = RAGEngine()

        # Load existing graph (use absolute path)
        gp_copilot_root = Path(__file__).parent.parent.parent
        self.graph_file = gp_copilot_root / "GP-DATA" / "knowledge-base" / "security_graph.pkl"
        self.load_graph()

        self.stats = {
            "nodes_added": 0,
            "edges_added": 0,
            "relationships_created": 0
        }

    def load_graph(self):
        """Load existing knowledge graph or create new one"""
        if self.graph_file.exists():
            print(f"📂 Loading existing knowledge graph from {self.graph_file}")
            with open(self.graph_file, 'rb') as f:
                data = pickle.load(f)
                self.graph = data['graph']
                self.node_types = data.get('node_types', {})
            print(f"   Loaded: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        else:
            print(f"📂 Creating new knowledge graph")
            self.graph = nx.MultiDiGraph()
            self.node_types = {}

    def save_graph(self):
        """Save knowledge graph to disk"""
        if self.dry_run:
            print(f"🔍 [DRY RUN] Would save graph to {self.graph_file}")
            return

        self.graph_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.graph_file, 'wb') as f:
            pickle.dump({
                'graph': self.graph,
                'node_types': self.node_types,
                'last_updated': datetime.now().isoformat()
            }, f)
        print(f"💾 Saved knowledge graph: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")

    def add_node(self, node_id: str, node_type: str, attributes: Dict[str, Any]):
        """Add node to graph with type tracking"""
        if not self.dry_run:
            # Copy attributes and ensure type is set correctly
            node_attrs = attributes.copy()
            node_attrs['type'] = node_type
            self.graph.add_node(node_id, **node_attrs)
            if node_type not in self.node_types:
                self.node_types[node_type] = set()
            self.node_types[node_type].add(node_id)
        self.stats["nodes_added"] += 1

    def add_edge(self, source: str, target: str, edge_type: str, attributes: Dict[str, Any] = None):
        """Add directed edge with type"""
        if attributes is None:
            attributes = {}
        if not self.dry_run:
            self.graph.add_edge(source, target, type=edge_type, **attributes)
        self.stats["edges_added"] += 1

    def extract_cks_knowledge(self) -> List[Dict]:
        """Extract CKS knowledge from RAG"""
        print(f"\n🔍 Extracting CKS knowledge from cks_knowledge collection...")

        # Get all CKS documents
        collection = self.rag_engine.cks_knowledge
        results = collection.get()

        cks_nodes = []
        for i, (doc_id, doc, metadata) in enumerate(zip(results['ids'], results['documents'], results['metadatas'])):
            # Extract question from content
            question = metadata.get('question', '')
            if not question:
                # Try to extract from document
                lines = doc.split('\n')
                for line in lines:
                    if line.startswith('Question:'):
                        question = line.replace('Question:', '').strip()
                        break

            node_data = {
                'id': doc_id,
                'type': 'cks_concept',
                'content': doc[:500],  # Truncate for graph storage
                'question': question,
                'metadata': metadata
            }
            cks_nodes.append(node_data)

        print(f"   Found {len(cks_nodes)} CKS concepts")
        return cks_nodes

    def extract_opa_knowledge(self) -> List[Dict]:
        """Extract OPA knowledge from RAG"""
        print(f"\n🔍 Extracting OPA knowledge from compliance_frameworks collection...")

        collection = self.rag_engine.compliance_frameworks
        results = collection.get()

        opa_nodes = []
        for i, (doc_id, doc, metadata) in enumerate(zip(results['ids'], results['documents'], results['metadatas'])):
            title = metadata.get('title', doc_id)
            topics = metadata.get('topic', '').split(', ') if metadata.get('topic') else []

            node_data = {
                'id': doc_id,
                'type': 'opa_policy' if 'policy' in title.lower() or 'rego' in title.lower() else 'opa_concept',
                'title': title,
                'content': doc[:500],
                'topics': topics,
                'metadata': metadata
            }
            opa_nodes.append(node_data)

        print(f"   Found {len(opa_nodes)} OPA concepts/policies")
        return opa_nodes

    def extract_cloud_patterns(self) -> List[Dict]:
        """Extract cloud/DevSecOps patterns from RAG"""
        print(f"\n🔍 Extracting cloud patterns from security_patterns collection...")

        collection = self.rag_engine.security_patterns
        results = collection.get()

        pattern_nodes = []
        for i, (doc_id, doc, metadata) in enumerate(zip(results['ids'], results['documents'], results['metadatas'])):
            # Extract question
            question = metadata.get('question', '')
            if not question:
                lines = doc.split('\n')
                for line in lines:
                    if line.startswith('Question:'):
                        question = line.replace('Question:', '').strip()
                        break

            # Classify pattern type
            pattern_type = 'devops_pattern'
            if 'argocd' in question.lower() or 'argocd' in doc.lower():
                pattern_type = 'argocd_pattern'
            elif 'helm' in question.lower() or 'helm' in doc.lower():
                pattern_type = 'helm_pattern'
            elif 'kubernetes' in question.lower() or 'k8s' in question.lower():
                pattern_type = 'k8s_pattern'

            node_data = {
                'id': doc_id,
                'type': pattern_type,
                'question': question,
                'content': doc[:500],
                'metadata': metadata
            }
            pattern_nodes.append(node_data)

        print(f"   Found {len(pattern_nodes)} cloud/DevOps patterns")
        return pattern_nodes

    def create_cis_benchmark_relationships(self, cks_nodes: List[Dict], opa_nodes: List[Dict]):
        """Create relationships between CKS/OPA and CIS benchmarks"""
        print(f"\n🔗 Creating CIS Benchmark relationships...")

        # Map common CIS benchmarks
        cis_benchmarks = {
            'CIS-5.1.3': 'Minimize wildcard use in Roles and ClusterRoles',
            'CIS-5.2.1': 'Minimize privileged containers',
            'CIS-5.2.6': 'Minimize admission of root containers',
            'CIS-5.7.1': 'Create network policies',
            'CIS-1.2.15': 'Enable audit logs',
        }

        # Add CIS nodes
        for cis_id, description in cis_benchmarks.items():
            self.add_node(
                cis_id,
                'cis_benchmark',
                {'description': description, 'framework': 'CIS Kubernetes v1.9'}
            )

        # Link CKS concepts to CIS
        cis_mapping = {
            'rbac': 'CIS-5.1.3',
            'privileged': 'CIS-5.2.1',
            'root': 'CIS-5.2.6',
            'network policy': 'CIS-5.7.1',
            'audit': 'CIS-1.2.15'
        }

        for node in cks_nodes:
            content_lower = node['content'].lower()
            for keyword, cis_id in cis_mapping.items():
                if keyword in content_lower:
                    self.add_edge(
                        node['id'],
                        cis_id,
                        'maps_to',
                        {'confidence': 'high', 'reason': f'Contains {keyword}'}
                    )
                    self.stats["relationships_created"] += 1

        # Link OPA policies to CIS
        for node in opa_nodes:
            content_lower = node['content'].lower() + node['title'].lower()
            for keyword, cis_id in cis_mapping.items():
                if keyword in content_lower:
                    self.add_edge(
                        node['id'],
                        cis_id,
                        'validates',
                        {'confidence': 'high', 'reason': f'Policy checks {keyword}'}
                    )
                    self.stats["relationships_created"] += 1

    def create_owasp_relationships(self, pattern_nodes: List[Dict]):
        """Create relationships to OWASP categories"""
        print(f"\n🔗 Creating OWASP relationships...")

        # Common OWASP categories
        owasp_categories = {
            'OWASP:A01:2021': 'Broken Access Control',
            'OWASP:A03:2021': 'Injection',
            'OWASP:A05:2021': 'Security Misconfiguration',
            'OWASP:A07:2021': 'Identification and Authentication Failures',
        }

        # Add OWASP nodes if they don't exist
        for owasp_id, description in owasp_categories.items():
            if not self.graph.has_node(owasp_id):
                self.add_node(
                    owasp_id,
                    'owasp_category',
                    {'description': description, 'framework': 'OWASP Top 10 2021'}
                )

        # Link patterns to OWASP
        owasp_mapping = {
            'rbac': 'OWASP:A01:2021',
            'authentication': 'OWASP:A07:2021',
            'secret': 'OWASP:A05:2021',
            'injection': 'OWASP:A03:2021'
        }

        for node in pattern_nodes:
            content_lower = node['content'].lower()
            for keyword, owasp_id in owasp_mapping.items():
                if keyword in content_lower:
                    self.add_edge(
                        node['id'],
                        owasp_id,
                        'categorized_as',
                        {'confidence': 'medium', 'reason': f'Related to {keyword}'}
                    )
                    self.stats["relationships_created"] += 1

    def create_knowledge_relationships(self, cks_nodes: List[Dict], opa_nodes: List[Dict], pattern_nodes: List[Dict]):
        """Create relationships between knowledge nodes"""
        print(f"\n🔗 Creating cross-knowledge relationships...")

        # Link OPA policies to CKS concepts (e.g., RBAC policy → RBAC concept)
        for opa_node in opa_nodes:
            opa_content = opa_node['content'].lower() + opa_node['title'].lower()

            for cks_node in cks_nodes:
                cks_content = cks_node['content'].lower()

                # Find common concepts
                common_keywords = ['rbac', 'pod security', 'network policy', 'audit', 'admission control']
                for keyword in common_keywords:
                    if keyword in opa_content and keyword in cks_content:
                        self.add_edge(
                            opa_node['id'],
                            cks_node['id'],
                            'implements',
                            {'concept': keyword, 'confidence': 'high'}
                        )
                        self.stats["relationships_created"] += 1
                        break  # Only one edge per pair

        # Link cloud patterns to CKS concepts
        for pattern_node in pattern_nodes:
            pattern_content = pattern_node['content'].lower()

            for cks_node in cks_nodes:
                cks_content = cks_node['content'].lower()

                # Find common Kubernetes concepts
                k8s_keywords = ['deployment', 'service', 'pod', 'namespace', 'configmap', 'secret']
                for keyword in k8s_keywords:
                    if keyword in pattern_content and keyword in cks_content:
                        self.add_edge(
                            pattern_node['id'],
                            cks_node['id'],
                            'applies_to',
                            {'resource': keyword, 'confidence': 'medium'}
                        )
                        self.stats["relationships_created"] += 1
                        break

    def build_graph(self):
        """Main graph building pipeline"""
        print(f"\n{'='*60}")
        print(f"🏗️  Building Knowledge Graph from RAG Vectors")
        print(f"{'='*60}")

        # Extract knowledge from RAG collections
        cks_nodes = self.extract_cks_knowledge()
        opa_nodes = self.extract_opa_knowledge()
        pattern_nodes = self.extract_cloud_patterns()

        # Add nodes to graph
        print(f"\n📝 Adding nodes to graph...")
        for node in cks_nodes:
            self.add_node(node['id'], node['type'], node)

        for node in opa_nodes:
            self.add_node(node['id'], node['type'], node)

        for node in pattern_nodes:
            self.add_node(node['id'], node['type'], node)

        # Create relationships
        self.create_cis_benchmark_relationships(cks_nodes, opa_nodes)
        self.create_owasp_relationships(pattern_nodes)
        self.create_knowledge_relationships(cks_nodes, opa_nodes, pattern_nodes)

        # Save graph
        self.save_graph()

        # Print summary
        print(f"\n{'='*60}")
        print(f"📊 Knowledge Graph Build Summary:")
        print(f"{'='*60}")
        print(f"  Nodes added: {self.stats['nodes_added']}")
        print(f"  Edges added: {self.stats['edges_added']}")
        print(f"  Relationships created: {self.stats['relationships_created']}")
        print(f"\n  Final graph size:")
        print(f"    Total nodes: {self.graph.number_of_nodes()}")
        print(f"    Total edges: {self.graph.number_of_edges()}")

        if self.dry_run:
            print(f"\n🔍 DRY RUN MODE - No changes saved")
        else:
            print(f"\n✅ Knowledge graph updated and saved")


def main():
    parser = argparse.ArgumentParser(
        description="Build knowledge graph from RAG vectors with semantic relationships"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be added without modifying graph"
    )

    args = parser.parse_args()

    builder = KnowledgeGraphBuilder(dry_run=args.dry_run)
    builder.build_graph()


if __name__ == "__main__":
    main()
