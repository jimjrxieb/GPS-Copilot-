#!/usr/bin/env python3
"""
Jade API - Web API for AI Security Consultant
REST endpoints for integration with GP-Copilot tools
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# Add project paths
sys.path.append(str(Path(__file__).parent / "pipelines"))

try:
    from langchain_chroma import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain.schema import Document
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install with: pip install flask flask-cors langchain-chroma langchain-community")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global Jade instance
jade_consultant = None

class JadeAPI:
    """Jade API wrapper for web interface"""

    def __init__(self, vector_db_path: Optional[Path] = None):
        print("🤖 Initializing Jade API...")

        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Connect to knowledge base
        if not vector_db_path:
            vector_db_path = Path(__file__).parent / "vector-db" / "gp_security_rag"

        self.vector_store = Chroma(
            persist_directory=str(vector_db_path),
            embedding_function=self.embeddings
        )

        self.specialties = [
            "Terraform Security & IaC",
            "Kubernetes Security (CKS)",
            "Policy as Code (OPA/Rego)",
            "Container Security",
            "Cloud Security",
            "Compliance (CCSP/CIS/NIST)"
        ]

    def search_knowledge(self, query: str, k: int = 5) -> List[Document]:
        """Search knowledge base"""
        return self.vector_store.similarity_search(query, k=k)

    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze security query for context"""
        query_lower = query.lower()

        analysis = {
            "domains": [],
            "tools": [],
            "urgency": "medium",
            "compliance": []
        }

        # Domain detection
        if any(term in query_lower for term in ["terraform", "iac"]):
            analysis["domains"].append("Infrastructure as Code")
        if any(term in query_lower for term in ["kubernetes", "k8s", "container"]):
            analysis["domains"].append("Kubernetes Security")
        if any(term in query_lower for term in ["opa", "rego", "policy"]):
            analysis["domains"].append("Policy as Code")

        # Tool detection
        tools = ["trivy", "checkov", "tfsec", "bandit", "semgrep", "falco"]
        for tool in tools:
            if tool in query_lower:
                analysis["tools"].append(tool)

        return analysis

    def generate_answer(self, query: str) -> Dict[str, Any]:
        """Generate comprehensive answer to security query"""

        # Search knowledge base
        docs = self.search_knowledge(query, k=5)
        analysis = self.analyze_query(query)

        if not docs:
            return {
                "answer": "I don't have specific information about that topic. Could you provide more context or rephrase your question?",
                "sources": [],
                "analysis": analysis,
                "confidence": 0.0
            }

        # Primary answer from best match
        primary_doc = docs[0]
        primary_content = primary_doc.page_content[:1500]

        # Build answer
        answer = f"Based on my security expertise:\n\n{primary_content}"

        if analysis["domains"]:
            answer += f"\n\n**Security Domains**: {', '.join(analysis['domains'])}"

        if analysis["tools"]:
            answer += f"\n**Relevant Tools**: {', '.join(analysis['tools'])}"

        # Source metadata
        sources = []
        for doc in docs[:3]:
            source_info = {
                "file": Path(doc.metadata.get('source', 'Unknown')).name,
                "type": doc.metadata.get('doc_type', 'Unknown'),
                "preview": doc.page_content[:200] + "..."
            }
            sources.append(source_info)

        confidence = min(0.9, len(docs) * 0.2)  # Simple confidence scoring

        return {
            "answer": answer,
            "sources": sources,
            "analysis": analysis,
            "confidence": confidence
        }

# Web interface template
WEB_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>Jade - AI Security Consultant</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .chat-container { border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .input-area { margin-bottom: 20px; }
        .input-area input { width: 80%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .input-area button { padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .response { background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; }
        .sources { background: #e9ecef; padding: 10px; border-radius: 4px; margin-top: 10px; font-size: 0.9em; }
        .loading { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Jade - AI Security Consultant</h1>
        <p>Enterprise Security Expert | Terraform • Kubernetes • Policy as Code • Compliance</p>
    </div>

    <div class="chat-container">
        <div class="input-area">
            <input type="text" id="queryInput" placeholder="Ask me about security architecture, tools, or best practices..." />
            <button onclick="askJade()">Ask Jade</button>
        </div>

        <div id="responses"></div>
    </div>

    <script>
        function askJade() {
            const query = document.getElementById('queryInput').value;
            if (!query.trim()) return;

            const responsesDiv = document.getElementById('responses');

            // Show user question
            responsesDiv.innerHTML += `
                <div style="text-align: right; margin: 10px 0;">
                    <strong>You:</strong> ${query}
                </div>
            `;

            // Show loading
            responsesDiv.innerHTML += `
                <div class="loading" id="loading">🤖 Jade is analyzing your question...</div>
            `;

            // Call API
            fetch('/api/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').remove();

                responsesDiv.innerHTML += `
                    <div class="response">
                        <strong>🤖 Jade:</strong><br>
                        <pre style="white-space: pre-wrap; font-family: Arial;">${data.answer}</pre>

                        <div class="sources">
                            <strong>📚 Sources:</strong><br>
                            ${data.sources.map(s => `• [${s.type}] ${s.file}`).join('<br>')}
                            <br><br>
                            <strong>Confidence:</strong> ${(data.confidence * 100).toFixed(0)}%
                        </div>
                    </div>
                `;

                responsesDiv.scrollTop = responsesDiv.scrollHeight;
            })
            .catch(error => {
                document.getElementById('loading').remove();
                responsesDiv.innerHTML += `
                    <div class="response" style="background: #f8d7da;">
                        <strong>❌ Error:</strong> ${error.message}
                    </div>
                `;
            });

            document.getElementById('queryInput').value = '';
        }

        // Enter key support
        document.getElementById('queryInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') askJade();
        });
    </script>
</body>
</html>
"""

# API Routes
@app.route('/')
def index():
    """Web interface"""
    return render_template_string(WEB_INTERFACE)

@app.route('/api/status')
def status():
    """API status endpoint"""
    return jsonify({
        "status": "active",
        "consultant": "Jade",
        "specialties": jade_consultant.specialties if jade_consultant else [],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/ask', methods=['POST'])
def ask():
    """Main consultation endpoint"""
    if not jade_consultant:
        return jsonify({"error": "Jade not initialized"}), 500

    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing query parameter"}), 400

    query = data['query'].strip()
    if not query:
        return jsonify({"error": "Empty query"}), 400

    try:
        # Generate answer
        result = jade_consultant.generate_answer(query)

        # Log consultation
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "confidence": result["confidence"],
            "sources_count": len(result["sources"])
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Consultation failed: {str(e)}"}), 500

@app.route('/api/search', methods=['POST'])
def search():
    """Direct knowledge base search"""
    if not jade_consultant:
        return jsonify({"error": "Jade not initialized"}), 500

    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing query parameter"}), 400

    try:
        docs = jade_consultant.search_knowledge(data['query'], k=data.get('limit', 5))

        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content[:500] + "...",
                "source": Path(doc.metadata.get('source', 'Unknown')).name,
                "type": doc.metadata.get('doc_type', 'Unknown')
            })

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

def initialize_jade():
    """Initialize Jade consultant"""
    global jade_consultant
    try:
        print("🚀 Initializing Jade API...")
        jade_consultant = JadeAPI()
        print("✅ Jade ready for consultations!")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Jade: {e}")
        return False

if __name__ == '__main__':
    if initialize_jade():
        print("\n🌐 Starting Jade API Server...")
        print("📍 Access at: http://localhost:5000")
        print("📚 API docs: http://localhost:5000/api/status")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        sys.exit(1)