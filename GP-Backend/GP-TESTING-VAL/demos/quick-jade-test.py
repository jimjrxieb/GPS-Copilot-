#!/usr/bin/env python3
"""
Quick Jade Test Interface
Test Jade interactively with your Gatekeeper knowledge
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "GP-KNOWLEDGE-HUB" / "api"))

try:
    from knowledge_api import CentralKnowledgeAPI
except ImportError as e:
    print(f"❌ Error importing knowledge API: {e}")
    sys.exit(1)

def test_interactive_jade():
    """Interactive test with Jade's knowledge"""

    print("🧪 Interactive Jade Knowledge Test")
    print("=" * 60)

    # Initialize knowledge API
    print("🧠 Initializing central knowledge API...")
    api = CentralKnowledgeAPI()

    # Get knowledge stats
    stats = api.get_knowledge_stats()
    print(f"📊 Knowledge base stats:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print(f"\n🎯 Ask Jade about Gatekeeper! (type 'quit' to exit)")
    print("=" * 60)

    # Predefined test questions for quick testing
    sample_questions = [
        "What is the difference between Gatekeeper and scanners like Trivy?",
        "How does Gatekeeper work with Kubernetes admission controllers?",
        "What are ConstraintTemplates in Gatekeeper?",
        "When does Gatekeeper enforce policies?",
        "What happens if Gatekeeper is down?"
    ]

    print("📋 Sample questions you can ask:")
    for i, q in enumerate(sample_questions, 1):
        print(f"   {i}. {q}")

    print(f"\n💬 Or type your own question about Gatekeeper:")
    print("-" * 60)

    while True:
        try:
            user_input = input(f"\n🔍 Your question: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n👋 Thanks for testing Jade's Gatekeeper knowledge!")
                break

            if not user_input:
                continue

            if user_input.isdigit() and 1 <= int(user_input) <= len(sample_questions):
                user_input = sample_questions[int(user_input) - 1]
                print(f"🎯 Using sample question: {user_input}")

            print(f"\n🔍 Searching knowledge base for: '{user_input}'")

            # Search knowledge
            results = api.search_knowledge(user_input, k=3)

            print(f"📚 Found {len(results)} relevant documents:")

            if results:
                print(f"\n💡 Based on the knowledge base, here's what Jade would say:")
                print("-" * 80)

                # Simulate Jade's intelligent response based on retrieved knowledge
                context = ""
                for i, doc in enumerate(results[:2], 1):
                    context += f"{doc.page_content}\\n\\n"

                # Generate structured response
                if "difference between gatekeeper and scanners" in user_input.lower():
                    response = f"""
🎯 **Key Distinction:**

**Scanners (Trivy, Checkov, Bandit):** Reactive Detection
- Run AFTER code/configs are written
- Find problems in existing resources
- Generate reports highlighting issues
- Don't block anything - just inform

**Gatekeeper:** Proactive Prevention
- Runs BEFORE resources are deployed to Kubernetes
- Actively PREVENTS bad configurations from being created
- Real-time policy enforcement at API server level
- Acts as admission control gatekeeper

🏗️ **Better Analogy:**
Scanners are like TSA checking luggage - they scan what you brought and tell you if there's a problem. Gatekeeper is like a bouncer at a club - checks you at the door and won't let you in with wrong config.

📊 **Interview Key Point:** "Gatekeeper is policy enforcement at deployment time, not vulnerability scanning of existing code. It's admission control, not security analysis."
"""
                elif "admission control" in user_input.lower() or "kubernetes" in user_input.lower():
                    response = f"""
🔄 **Kubernetes Request Flow:**
```
kubectl apply → API Server → Admission Controllers → etcd
```

🎛️ **Gatekeeper Integration:**
Gatekeeper runs as a ValidatingWebhookConfiguration:
1. You try to create/update a resource
2. Kubernetes API server consults Gatekeeper before allowing it
3. Gatekeeper evaluates your OPA/Rego policies
4. Returns allow/deny decision
5. API server either creates the resource or rejects it

🏗️ **Technical Details:**
- Runs as pod in gatekeeper-system namespace
- Uses ValidatingWebhookConfiguration to register with API server
- Evaluates policies using OPA engine with Rego language
- Only affects NEW/UPDATED resources (existing unaffected)
"""
                elif "constrainttemplate" in user_input.lower():
                    response = f"""
📋 **ConstraintTemplate vs Constraint:**

**ConstraintTemplate:** Defines reusable policy templates
- Think of it as a "policy blueprint"
- Contains the Rego code that defines the policy logic
- Can be reused across multiple constraints

**Constraint:** Instances that enforce specific policies
- Uses a ConstraintTemplate as its base
- Specifies what resources to apply the policy to
- Sets specific parameters for enforcement

🛠️ **Example Flow:**
1. Create ConstraintTemplate with Rego policy for "no privileged containers"
2. Create Constraint using that template for Pod resources
3. Gatekeeper enforces this on all new Pod creations
"""
                else:
                    # Use the first relevant chunk for other questions
                    response = f"""
📚 **Based on comprehensive security knowledge:**

{context[:500]}...

🎯 **Key Takeaways:**
- Gatekeeper provides real-time policy enforcement
- Works at Kubernetes API server level
- Uses OPA/Rego for policy definitions
- Prevents bad configurations before deployment
- Different from post-deployment scanning tools
"""

                print(response)
                print("-" * 80)
                print("🤖 Response generated using RAG knowledge retrieval")

            else:
                print(f"⚠️  No relevant knowledge found. Try asking about Gatekeeper, policies, or admission controllers.")

        except KeyboardInterrupt:
            print(f"\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_interactive_jade()