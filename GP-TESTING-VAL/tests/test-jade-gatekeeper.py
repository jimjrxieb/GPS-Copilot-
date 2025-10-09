#!/usr/bin/env python3
"""
Test Jade's Knowledge About Gatekeeper
Test the RAG → Embedding → Jade pipeline
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "GP-RAG"))

try:
    from jade_live import JadeSecurityConsultant
except ImportError as e:
    print(f"Error importing Jade: {e}")
    sys.exit(1)

def test_jade_gatekeeper_knowledge():
    """Test Jade's understanding of Gatekeeper"""

    print("🧪 Testing Jade's Gatekeeper Knowledge")
    print("=" * 60)

    # Initialize Jade with shorter timeout since we want to see results quickly
    print("🤖 Initializing Jade...")
    jade = JadeSecurityConsultant()

    # Test queries about Gatekeeper
    gatekeeper_questions = [
        "What is the difference between Gatekeeper and scanners like Trivy?",
        "How does Gatekeeper work with Kubernetes admission controllers?",
        "What are ConstraintTemplates and Constraints in Gatekeeper?",
        "When does Gatekeeper enforce policies - before or after deployment?",
        "What is the difference between OPA and Gatekeeper?"
    ]

    print(f"\n🔍 Testing {len(gatekeeper_questions)} Gatekeeper questions...")

    for i, question in enumerate(gatekeeper_questions, 1):
        print(f"\n" + "="*80)
        print(f"🔍 Question {i}: {question}")
        print("-" * 80)

        try:
            # Search knowledge base for relevant documents
            docs = jade.search_knowledge(question, k=3)
            print(f"📚 Found {len(docs)} relevant documents from knowledge base")

            # Analyze context
            context = jade.analyze_security_context(question)
            print(f"📊 Security domains identified: {context.get('domains', [])}")

            # Generate response (this will use local Qwen2.5-7B if available)
            print(f"🤖 Generating response...")
            response = jade.generate_response(question, docs, context)

            # Display response
            print(f"\n💬 Jade's Response:")
            print("-" * 60)
            print(response)
            print("-" * 60)

            # Check if Qwen was used or fallback
            if "local Qwen2.5-7B model" in response:
                print("✅ Response generated using local Qwen2.5-7B model")
            elif "enterprise security knowledge base" in response:
                print("⚠️  Response generated using fallback (knowledge base only)")
            else:
                print("❓ Unknown response generation method")

        except Exception as e:
            print(f"❌ Error processing question: {e}")

        print(f"\n{'='*80}")

    print(f"\n🎯 Gatekeeper Knowledge Test Complete!")
    print("📊 Results show whether Jade can correctly explain:")
    print("   - Difference between scanners vs admission control")
    print("   - How Gatekeeper integrates with Kubernetes")
    print("   - OPA vs Gatekeeper relationship")
    print("   - Policy enforcement timing")

if __name__ == "__main__":
    test_jade_gatekeeper_knowledge()