#!/usr/bin/env python3
"""
Jade RAG + LangGraph - Senior Security Consultant AI
Combines RAG for knowledge retrieval with LangGraph for advanced reasoning

This bypasses fine-tuning limitations by using:
1. Vector database with security expertise
2. LangGraph for multi-step reasoning
3. Base Qwen2.5-7B for generation
"""

import sys
import json
from pathlib import Path
from typing import TypedDict, List, Dict, Any, Annotated
import operator

try:
    from langgraph.graph import StateGraph, END
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain_community.llms import HuggingFacePipeline
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install: pip install langgraph langchain chromadb sentence-transformers transformers")
    sys.exit(1)


class JadeState(TypedDict):
    """Agent state for LangGraph workflow"""
    query: str
    domain: str  # CVE, code_review, kubernetes, terraform, etc.
    retrieved_knowledge: List[Dict]
    reasoning_chain: List[str]
    draft_response: str
    final_response: str
    sources: List[str]
    confidence: float


class JadeRAGAgent:
    """Advanced Security Consultant using RAG + LangGraph"""

    def __init__(self, vector_db_path: str = "./jade_vector_db"):
        print("🤖 Initializing Jade RAG + LangGraph Agent...")

        self.vector_db_path = vector_db_path

        # Initialize embeddings (CPU only for RTX 5080 compatibility)
        print("📊 Loading embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )

        # Initialize vector store
        self.vector_store = self._load_vector_store()

        # Initialize LLM (Qwen2.5-7B)
        self.llm = self._initialize_llm()

        # Build LangGraph workflow
        self.workflow = self._build_workflow()

        print("✅ Jade RAG Agent ready!")

    def _load_vector_store(self):
        """Load or create vector store"""
        try:
            print(f"📦 Loading vector store from {self.vector_db_path}...")
            vector_store = Chroma(
                persist_directory=self.vector_db_path,
                embedding_function=self.embeddings
            )
            count = vector_store._collection.count()
            print(f"✅ Loaded vector store with {count} documents")
            return vector_store
        except Exception as e:
            print(f"⚠️  No existing vector store: {e}")
            print("💡 Creating new vector store...")
            vector_store = Chroma(
                persist_directory=self.vector_db_path,
                embedding_function=self.embeddings
            )
            return vector_store

    def _initialize_llm(self):
        """Initialize Qwen2.5-7B model"""
        try:
            print("🧠 Loading Qwen2.5-7B-Instruct...")

            model_name = "Qwen/Qwen2.5-7B-Instruct"

            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )

            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.bfloat16,
                device_map="auto",
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )

            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=1024,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )

            print("✅ Qwen2.5-7B loaded successfully")
            return HuggingFacePipeline(pipeline=pipe)

        except Exception as e:
            print(f"❌ Error loading Qwen: {e}")
            print("⚠️  Jade will use retrieval-only mode")
            return None

    def _build_workflow(self):
        """Build LangGraph workflow for security analysis"""
        workflow = StateGraph(JadeState)

        # Define nodes
        workflow.add_node("classify_domain", self.classify_domain)
        workflow.add_node("retrieve_knowledge", self.retrieve_knowledge)
        workflow.add_node("reason_about_security", self.reason_about_security)
        workflow.add_node("draft_response", self.draft_response)
        workflow.add_node("enhance_response", self.enhance_response)
        workflow.add_node("finalize", self.finalize)

        # Define edges
        workflow.set_entry_point("classify_domain")
        workflow.add_edge("classify_domain", "retrieve_knowledge")
        workflow.add_edge("retrieve_knowledge", "reason_about_security")
        workflow.add_edge("reason_about_security", "draft_response")
        workflow.add_edge("draft_response", "enhance_response")
        workflow.add_edge("enhance_response", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile()

    def classify_domain(self, state: JadeState) -> JadeState:
        """Classify the security domain of the query"""
        query = state["query"].lower()

        if "cve" in query or "vulnerability" in query or "exploit" in query:
            domain = "cve_analysis"
        elif "kubernetes" in query or "k8s" in query or "pod" in query or "opa" in query:
            domain = "kubernetes_security"
        elif "terraform" in query or "cloudformation" in query or "iac" in query:
            domain = "iac_security"
        elif "code" in query or "bandit" in query or "semgrep" in query:
            domain = "code_security"
        elif "docker" in query or "container" in query:
            domain = "container_security"
        else:
            domain = "general_security"

        state["domain"] = domain
        state["reasoning_chain"] = [f"Classified query as: {domain}"]
        return state

    def retrieve_knowledge(self, state: JadeState) -> JadeState:
        """Retrieve relevant knowledge from vector store"""
        query = state["query"]
        domain = state["domain"]

        # Enhance query with domain context
        enhanced_query = f"{domain}: {query}"

        try:
            # Retrieve top 5 most relevant documents
            results = self.vector_store.similarity_search_with_score(
                enhanced_query,
                k=5
            )

            retrieved_knowledge = []
            sources = []

            for doc, score in results:
                retrieved_knowledge.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": float(score)
                })
                sources.append(doc.metadata.get("source", "unknown"))

            state["retrieved_knowledge"] = retrieved_knowledge
            state["sources"] = sources
            state["reasoning_chain"].append(
                f"Retrieved {len(retrieved_knowledge)} relevant knowledge documents"
            )

        except Exception as e:
            print(f"⚠️  Retrieval error: {e}")
            state["retrieved_knowledge"] = []
            state["sources"] = []

        return state

    def reason_about_security(self, state: JadeState) -> JadeState:
        """Apply security reasoning to the query"""
        domain = state["domain"]
        retrieved = state["retrieved_knowledge"]

        # Extract key security concepts from retrieved knowledge
        security_concepts = []

        for doc in retrieved:
            content = doc["content"]

            # Extract severity indicators
            if "CRITICAL" in content:
                security_concepts.append("critical_severity")
            if "HIGH" in content or "High" in content:
                security_concepts.append("high_severity")

            # Extract security domains
            if "CVE-" in content:
                security_concepts.append("cve_present")
            if "remediation" in content.lower():
                security_concepts.append("remediation_available")
            if "exploit" in content.lower():
                security_concepts.append("exploit_info")

        reasoning = f"Security analysis for {domain}. "
        reasoning += f"Found {len(set(security_concepts))} security indicators: {', '.join(set(security_concepts))}"

        state["reasoning_chain"].append(reasoning)
        return state

    def draft_response(self, state: JadeState) -> JadeState:
        """Generate initial response using LLM + retrieved knowledge"""
        query = state["query"]
        domain = state["domain"]
        knowledge = state["retrieved_knowledge"]

        # Build context from retrieved knowledge
        context = "\n\n".join([
            f"Knowledge {i+1}:\n{doc['content'][:500]}"
            for i, doc in enumerate(knowledge[:3])  # Top 3 documents
        ])

        # Build prompt
        system_prompt = """You are Jade, a senior security consultant AI specializing in vulnerability analysis, code security, and remediation strategies. You provide detailed, actionable security assessments with business context."""

        user_prompt = f"""Based on the following security knowledge, answer this query:

Query: {query}

Relevant Security Knowledge:
{context}

Provide a comprehensive security analysis including:
1. Technical analysis
2. Business impact
3. Remediation strategy
4. References to specific CVEs, tools, or standards mentioned
"""

        if self.llm:
            try:
                # Generate response
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = self.llm(full_prompt)
                state["draft_response"] = response
                state["reasoning_chain"].append("Generated LLM response")
            except Exception as e:
                print(f"⚠️  LLM generation error: {e}")
                # Fallback: use retrieved knowledge
                state["draft_response"] = self._create_fallback_response(state)
                state["reasoning_chain"].append("Used fallback response (LLM unavailable)")
        else:
            state["draft_response"] = self._create_fallback_response(state)
            state["reasoning_chain"].append("Used retrieval-only response")

        return state

    def _create_fallback_response(self, state: JadeState) -> str:
        """Create response from retrieved knowledge only"""
        knowledge = state["retrieved_knowledge"]

        response = f"# Security Analysis: {state['domain']}\n\n"
        response += f"## Query: {state['query']}\n\n"
        response += "## Relevant Security Information:\n\n"

        for i, doc in enumerate(knowledge[:3], 1):
            response += f"### Finding {i}:\n{doc['content'][:800]}\n\n"
            if 'metadata' in doc and doc['metadata']:
                response += f"**Source**: {doc['metadata'].get('source', 'N/A')}\n\n"

        response += "\n## Recommendations:\n"
        response += "Based on the retrieved security knowledge, please:\n"
        response += "1. Review the findings above carefully\n"
        response += "2. Cross-reference with official documentation\n"
        response += "3. Implement recommended remediations\n"
        response += "4. Test fixes in a safe environment\n"

        return response

    def enhance_response(self, state: JadeState) -> JadeState:
        """Enhance response with sources and confidence"""
        draft = state["draft_response"]
        sources = state["sources"]

        # Add sources section
        enhanced = draft + "\n\n---\n\n## Sources:\n"
        for i, source in enumerate(set(sources), 1):
            enhanced += f"{i}. {source}\n"

        # Calculate confidence based on retrieval quality
        knowledge = state["retrieved_knowledge"]
        if knowledge:
            avg_score = sum(doc["relevance_score"] for doc in knowledge) / len(knowledge)
            confidence = min(0.95, max(0.5, 1.0 - avg_score))  # Lower score = higher relevance
        else:
            confidence = 0.3

        state["final_response"] = enhanced
        state["confidence"] = confidence
        state["reasoning_chain"].append(f"Response confidence: {confidence:.2f}")

        return state

    def finalize(self, state: JadeState) -> JadeState:
        """Final processing and validation"""
        # Add reasoning chain to response for transparency
        state["final_response"] += "\n\n---\n\n## Analysis Process:\n"
        for step in state["reasoning_chain"]:
            state["final_response"] += f"- {step}\n"

        return state

    def query(self, question: str) -> Dict[str, Any]:
        """Process a security query through the RAG + LangGraph system"""
        initial_state: JadeState = {
            "query": question,
            "domain": "",
            "retrieved_knowledge": [],
            "reasoning_chain": [],
            "draft_response": "",
            "final_response": "",
            "sources": [],
            "confidence": 0.0
        }

        # Execute workflow
        result = self.workflow.invoke(initial_state)

        return {
            "response": result["final_response"],
            "confidence": result["confidence"],
            "domain": result["domain"],
            "sources": result["sources"],
            "reasoning": result["reasoning_chain"]
        }


def main():
    """Example usage"""
    print("=" * 80)
    print("Jade RAG + LangGraph Security Consultant")
    print("=" * 80)

    # Initialize agent
    agent = JadeRAGAgent()

    # Example queries
    test_queries = [
        "Analyze CVE-2024-33663 affecting python-jose",
        "How do I fix a Kubernetes pod rejected for running as root?",
        "What security issues does Bandit find in subprocess usage?"
    ]

    for query in test_queries:
        print(f"\n\n{'='*80}")
        print(f"Query: {query}")
        print('='*80)

        result = agent.query(query)

        print(f"\nDomain: {result['domain']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"\nResponse:\n{result['response']}")
        print("\n" + "="*80)


if __name__ == "__main__":
    main()