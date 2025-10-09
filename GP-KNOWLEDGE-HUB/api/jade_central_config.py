#!/usr/bin/env python3
"""
Jade Central Knowledge Configuration
Updates Jade to use the central knowledge hub
"""

# Central knowledge hub paths
CENTRAL_HUB_PATH = "/home/jimmie/linkops-industries/GP-copilot/GP-KNOWLEDGE-HUB"
CENTRAL_VECTOR_STORE_PATH = "/home/jimmie/linkops-industries/GP-copilot/GP-KNOWLEDGE-HUB/vector-store/central-knowledge-db"
CENTRAL_KNOWLEDGE_BASE_PATH = "/home/jimmie/linkops-industries/GP-copilot/GP-KNOWLEDGE-HUB/knowledge-base"

# Domain mappings
KNOWLEDGE_DOMAINS = {
    "security": "/home/jimmie/linkops-industries/GP-copilot/GP-KNOWLEDGE-HUB/knowledge-base/security",
    "compliance": "/home/jimmie/linkops-industries/GP-copilot/GP-KNOWLEDGE-HUB/knowledge-base/compliance",
    "tools": "/home/jimmie/linkops-industries/GP-copilot/GP-KNOWLEDGE-HUB/knowledge-base/tools",
    "workflows": "/home/jimmie/linkops-industries/GP-copilot/GP-KNOWLEDGE-HUB/knowledge-base/workflows",
    "policies": "/home/jimmie/linkops-industries/GP-copilot/GP-KNOWLEDGE-HUB/knowledge-base/policies"
}

def get_central_vector_store_path():
    """Get path to central vector store"""
    return CENTRAL_VECTOR_STORE_PATH

def get_knowledge_domain_path(domain: str):
    """Get path to specific knowledge domain"""
    return KNOWLEDGE_DOMAINS.get(domain)

def get_all_knowledge_paths():
    """Get all knowledge domain paths"""
    return list(KNOWLEDGE_DOMAINS.values())
