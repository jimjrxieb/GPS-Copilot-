"""
Complete AI Security Engine - Integration Layer
Combines RAG, LLM, and Security Analysis for Production Consulting
"""

import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# Import our components
from .rag_engine import rag_engine
from .security_reasoning import SecurityReasoningEngine, SecurityAssessment, SecurityFinding

# Import from parent directories
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from knowledge.comprehensive_jade_prompts import get_comprehensive_security_prompt, get_focused_scanner_prompt, ANALYSIS_PROFILES
except ImportError:
    print("⚠️  Jade prompts not available - using basic prompts")
    ANALYSIS_PROFILES = {}
    def get_comprehensive_security_prompt(depth="comprehensive"): return "Analyze for security issues"
    def get_focused_scanner_prompt(scanner="generic"): return "Scan for vulnerabilities"

try:
    from models.model_manager import model_manager
    AI_MODEL_AVAILABLE = True
except ImportError:
    AI_MODEL_AVAILABLE = False
    print("⚠️  Model manager not available - using enhanced pattern matching")

@dataclass
class AISecurityAnalysis:
    """Complete AI-powered security analysis result"""
    findings: List[SecurityFinding]
    ai_summary: str
    rag_context: List[Dict[str, Any]]
    compliance_guidance: str
    remediation_plan: List[str]
    confidence_score: float

class AISecurityEngine:
    """Complete AI-powered security consulting engine"""

    def __init__(self):
        print("🚀 Initializing AI Security Engine...")

        # Initialize components
        self.rag = rag_engine
        self.security_engine = SecurityReasoningEngine()

        # Load knowledge bases
        self._load_knowledge_bases()

        # Model status
        self.model_ready = AI_MODEL_AVAILABLE

        print(f"✅ AI Security Engine initialized")
        print(f"   RAG System: {len(self.rag.get_stats()['collections'])} collections")
        print(f"   LLM Model: {'Ready' if self.model_ready else 'Loading...'}")

    def _load_knowledge_bases(self):
        """Load all security knowledge bases"""
        # Load if not already loaded
        stats = self.rag.get_stats()
        if stats['total_documents'] == 0:
            self.rag.load_cks_knowledge()
            self.rag.load_compliance_frameworks()

    async def analyze_project(self, project_path: str, client_name: str, analysis_depth: str = "comprehensive", industry: str = None, compliance_requirements: list = None) -> AISecurityAnalysis:
        """Complete AI-powered project security analysis using comprehensive prompting"""
        print(f"🚀 Starting comprehensive Jade analysis for {client_name}...")

        # Generate comprehensive security consultant prompt
        comprehensive_prompt = get_comprehensive_security_prompt(
            project_path=project_path,
            client_name=client_name,
            analysis_depth=analysis_depth,
            industry=industry,
            compliance_requirements=compliance_requirements or ["SOC2", "CIS"]
        )

        # Use Jade's comprehensive prompting approach
        if self.model_ready and AI_MODEL_AVAILABLE:
            try:
                print("🧠 Executing comprehensive security analysis via Jade prompting...")

                # Get RAG context for the project
                project_context = self.rag.query_knowledge(f"security analysis for {client_name} project", n_results=5)

                # Enhance prompt with RAG context
                context_text = "\n".join([ctx["content"][:300] for ctx in project_context])
                enhanced_prompt = f"""SECURITY KNOWLEDGE CONTEXT:
{context_text}

{comprehensive_prompt}"""

                # Execute comprehensive analysis
                comprehensive_analysis = model_manager.query_security_knowledge(enhanced_prompt)

                # Extract structured findings from the comprehensive analysis
                assessment = await self._extract_findings_from_analysis(comprehensive_analysis, project_path, client_name)

                # Get additional RAG context for specific findings
                rag_context = await self._get_rag_context(assessment.findings)

                # Generate final remediation plan
                remediation_plan = await self._generate_remediation_plan(assessment.findings, rag_context)

                return AISecurityAnalysis(
                    findings=assessment.findings,
                    ai_summary=comprehensive_analysis,
                    rag_context=rag_context,
                    compliance_guidance=f"Analysis includes {', '.join(compliance_requirements or ['SOC2', 'CIS'])} compliance requirements",
                    remediation_plan=remediation_plan,
                    confidence_score=0.95  # High confidence from comprehensive prompting
                )

            except Exception as e:
                print(f"⚠️ Comprehensive prompting failed, falling back to traditional analysis: {e}")

        # Fallback to traditional analysis if comprehensive prompting fails
        print("🔄 Using traditional security analysis approach...")

        # 1. Ingest client project context
        self.rag.ingest_client_project(project_path, client_name)

        # 2. Run security analysis
        assessment = await self.security_engine.comprehensive_analysis(project_path, client_name)

        # 3. Get RAG context for findings
        rag_context = await self._get_rag_context(assessment.findings)

        # 4. Generate AI-enhanced summary
        ai_summary = await self._generate_ai_summary(assessment, rag_context)

        # 5. Generate compliance guidance
        compliance_guidance = await self._generate_compliance_guidance(assessment.findings)

        # 6. Create remediation plan
        remediation_plan = await self._generate_remediation_plan(assessment.findings, rag_context)

        # 7. Calculate confidence score
        confidence_score = self._calculate_confidence(assessment.findings)

        return AISecurityAnalysis(
            findings=assessment.findings,
            ai_summary=ai_summary,
            rag_context=rag_context,
            compliance_guidance=compliance_guidance,
            remediation_plan=remediation_plan,
            confidence_score=confidence_score
        )

    async def _get_rag_context(self, findings: List[SecurityFinding]) -> List[Dict[str, Any]]:
        """Get relevant knowledge from RAG for findings"""
        context = []

        # Get unique categories from findings
        categories = list(set(f.category for f in findings))

        for category in categories[:5]:  # Limit to top 5 categories
            query = f"Security best practices for {category.lower()}"
            results = self.rag.query_knowledge(query, knowledge_type="all", n_results=2)
            context.extend(results)

        return context

    async def _extract_findings_from_analysis(self, comprehensive_analysis: str, project_path: str, client_name: str) -> SecurityAssessment:
        """Extract structured findings from comprehensive AI analysis"""

        # For now, create a mock assessment with the AI analysis as summary
        # In production, you'd parse the comprehensive analysis to extract specific findings
        findings = [
            SecurityFinding(
                id="comprehensive_ai_001",
                severity="HIGH",
                category="AI Analysis",
                description="Comprehensive security analysis completed",
                file_path=project_path,
                line_number=None,
                impact="See detailed AI analysis for complete impact assessment",
                recommendation="Follow AI-generated remediation plan",
                compliance_frameworks=["SOC2", "CIS"],
                ai_confidence=0.95
            )
        ]

        return SecurityAssessment(
            project_name=client_name,
            files_analyzed=1,
            findings=findings,
            risk_level="MEDIUM",
            ai_summary=comprehensive_analysis[:500] + "..." if len(comprehensive_analysis) > 500 else comprehensive_analysis
        )

    async def _generate_ai_summary(self, assessment: SecurityAssessment, rag_context: List[Dict[str, Any]]) -> str:
        """Generate AI-enhanced summary with RAG context"""

        if self.model_ready and AI_MODEL_AVAILABLE:
            try:
                # Build context from RAG
                context_text = "\n".join([ctx["content"][:200] for ctx in rag_context[:3]])

                # Create comprehensive prompt
                prompt = f"""You are a senior security consultant. Analyze this security assessment:

Project: {assessment.project_name}
Files Analyzed: {assessment.files_analyzed}
Issues Found: {len(assessment.findings)}
Risk Level: {assessment.risk_level}

Key Issues:
{', '.join(list(set(f.category for f in assessment.findings[:5])))}

Security Knowledge Context:
{context_text}

Provide a professional executive summary focusing on business impact and strategic recommendations."""

                response = model_manager.query_security_knowledge(prompt)
                return response

            except Exception as e:
                print(f"AI summary generation failed: {e}")

        # Fallback to enhanced pattern-based summary
        return self._generate_enhanced_summary(assessment, rag_context)

    def _generate_enhanced_summary(self, assessment: SecurityAssessment, rag_context: List[Dict[str, Any]]) -> str:
        """Enhanced pattern-based summary with RAG context"""

        base_summary = assessment.ai_summary

        # Add RAG insights
        if rag_context:
            relevant_practices = []
            for ctx in rag_context[:2]:
                if ctx["distance"] < 0.3:  # High relevance
                    practice = ctx["content"].split('.')[0]  # First sentence
                    relevant_practices.append(practice)

            if relevant_practices:
                rag_guidance = f"\n\nBest Practice Recommendations: {' '.join(relevant_practices)}"
                base_summary += rag_guidance

        return base_summary

    async def _generate_compliance_guidance(self, findings: List[SecurityFinding]) -> str:
        """Generate compliance-specific guidance"""

        # Get compliance frameworks mentioned in findings
        frameworks = set()
        for finding in findings:
            if finding.compliance_frameworks:
                frameworks.update(finding.compliance_frameworks)

        if not frameworks:
            return "No specific compliance requirements identified."

        # Query RAG for compliance guidance
        guidance_parts = []
        for framework in list(frameworks)[:3]:
            query = f"{framework} compliance requirements security"
            results = self.rag.query_knowledge(query, knowledge_type="compliance", n_results=1)
            if results:
                guidance_parts.append(f"{framework}: {results[0]['content'][:200]}")

        return "\n".join(guidance_parts) if guidance_parts else "Review compliance requirements for identified frameworks."

    async def _generate_remediation_plan(self, findings: List[SecurityFinding], rag_context: List[Dict[str, Any]]) -> List[str]:
        """Generate prioritized remediation plan"""

        plan = []

        # Prioritize by severity
        critical_findings = [f for f in findings if f.severity == "CRITICAL"]
        high_findings = [f for f in findings if f.severity == "HIGH"]

        if critical_findings:
            plan.append(f"IMMEDIATE: Address {len(critical_findings)} critical vulnerabilities")

        if high_findings:
            plan.append(f"Week 1: Remediate {len(high_findings)} high-severity issues")

        # Add category-specific recommendations
        categories = list(set(f.category for f in findings))
        for category in categories[:3]:
            plan.append(f"Ongoing: Implement {category.lower()} security controls")

        # Add RAG-based recommendations
        for ctx in rag_context[:2]:
            if "implement" in ctx["content"].lower() or "use" in ctx["content"].lower():
                recommendation = ctx["content"].split('.')[0]
                if len(recommendation) < 100:
                    plan.append(f"Best Practice: {recommendation}")

        return plan[:6]  # Limit to 6 items

    def _calculate_confidence(self, findings: List[SecurityFinding]) -> float:
        """Calculate overall confidence score"""
        if not findings:
            return 0.95  # High confidence in clean projects

        # Average confidence from individual findings
        confidences = [f.ai_confidence for f in findings if f.ai_confidence > 0]
        if confidences:
            return sum(confidences) / len(confidences)
        else:
            return 0.75  # Default confidence for pattern-based analysis

    async def query_security_expert(self, question: str, client_context: Optional[str] = None) -> str:
        """Query the AI security expert with RAG context"""

        # Get relevant context from RAG
        rag_results = self.rag.query_knowledge(question, knowledge_type="all", n_results=3)
        context = "\n".join([r["content"][:300] for r in rag_results])

        if self.model_ready and AI_MODEL_AVAILABLE:
            try:
                enhanced_question = f"""Security Knowledge Context:
{context}

{f"Client Context: {client_context}" if client_context else ""}

Question: {question}

Provide a detailed security consultant response:"""

                response = model_manager.query_security_knowledge(enhanced_question)
                return response
            except Exception as e:
                print(f"AI query failed: {e}")

        # Fallback response with RAG context
        if rag_results:
            best_match = rag_results[0]
            return f"Based on security best practices: {best_match['content'][:500]}..."
        else:
            return "I can help with security analysis. Please provide more specific details about your security concern."

    def get_engine_status(self) -> Dict[str, Any]:
        """Get complete engine status"""
        rag_stats = self.rag.get_stats()

        return {
            "ai_model_ready": self.model_ready,
            "rag_system": {
                "status": "operational",
                "device": rag_stats["device"],
                "collections": rag_stats["collections"],
                "total_documents": rag_stats["total_documents"]
            },
            "security_engine": "operational",
            "capabilities": [
                "Project security analysis",
                "Compliance framework mapping",
                "AI-powered recommendations",
                "RAG-enhanced context",
                "Client project ingestion"
            ]
        }

# Global AI security engine
ai_security_engine = AISecurityEngine()

if __name__ == "__main__":
    async def test_engine():
        print("🧪 Testing Complete AI Security Engine...")

        # Test query
        response = await ai_security_engine.query_security_expert(
            "What are the most critical Kubernetes security misconfigurations?"
        )
        print(f"\n🤖 AI Response:\n{response}")

        # Engine status
        status = ai_security_engine.get_engine_status()
        print(f"\n📊 Engine Status:")
        print(f"AI Model: {'Ready' if status['ai_model_ready'] else 'Loading'}")
        print(f"RAG System: {status['rag_system']['status']}")
        print(f"Knowledge Base: {status['rag_system']['total_documents']} documents")
        print(f"Capabilities: {len(status['capabilities'])} features")

    asyncio.run(test_engine())