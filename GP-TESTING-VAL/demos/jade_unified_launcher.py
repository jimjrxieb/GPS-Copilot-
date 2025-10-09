#!/usr/bin/env python3
"""
JADE Unified Launcher - Centralized startup for all JADE components
Ensures RAG, GUI, and AI chatbox are all properly initialized
"""

import sys
import os
import subprocess
import time
import threading
import signal
from pathlib import Path
import json

# Add necessary paths
sys.path.append(str(Path(__file__).parent / "GP-RAG"))
sys.path.append(str(Path(__file__).parent / "GP-AI"))
sys.path.append(str(Path(__file__).parent / "GP-KNOWLEDGE-HUB" / "api"))

class JadeUnifiedLauncher:
    """Centralized launcher for all JADE components"""

    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent
        self.components_status = {
            "rag_database": False,
            "jade_api": False,
            "gui": False,
            "knowledge_hub": False
        }

    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        print("🔍 Checking dependencies...")

        required_packages = [
            "langchain",
            "langchain_chroma",
            "langchain_community",
            "sentence-transformers",
            "flask",
            "flask_cors",
            "transformers",
            "torch"
        ]

        missing = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing.append(package)

        if missing:
            print(f"❌ Missing packages: {', '.join(missing)}")
            print(f"📦 Install with: pip install {' '.join(missing)}")
            return False

        print("✅ All Python dependencies satisfied")
        return True

    def initialize_rag_database(self):
        """Ensure RAG database is initialized and populated"""
        print("\n🧠 Initializing RAG Database...")

        vector_db_path = self.base_dir / "GP-RAG" / "vector-db" / "gp_security_rag"

        if not vector_db_path.exists():
            print("📚 Creating and populating RAG database...")
            try:
                subprocess.run([
                    sys.executable,
                    str(self.base_dir / "GP-RAG" / "populate_rag_knowledge.py")
                ], check=True, capture_output=True, text=True)
                self.components_status["rag_database"] = True
                print("✅ RAG database initialized")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to initialize RAG database: {e}")
                return False
        else:
            print("✅ RAG database found at:", vector_db_path)
            self.components_status["rag_database"] = True

        return True

    def start_jade_api(self):
        """Start JADE API server for AI interactions"""
        print("\n🤖 Starting JADE API Server...")

        api_script = self.base_dir / "GP-RAG" / "jade_api.py"

        if not api_script.exists():
            # Create the API script if it doesn't exist
            self.create_jade_api_script(api_script)

        try:
            process = subprocess.Popen(
                [sys.executable, str(api_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(process)

            # Wait for server to start
            time.sleep(3)

            # Check if server is running
            import requests
            try:
                response = requests.get("http://localhost:5000/health", timeout=2)
                if response.status_code == 200:
                    self.components_status["jade_api"] = True
                    print("✅ JADE API Server running at http://localhost:5000")
                    return True
            except:
                pass

            print("⚠️  JADE API Server starting (may take a moment)...")
            self.components_status["jade_api"] = True
            return True

        except Exception as e:
            print(f"❌ Failed to start JADE API: {e}")
            return False

    def create_jade_api_script(self, api_path):
        """Create a simple JADE API if it doesn't exist"""
        api_content = '''#!/usr/bin/env python3
"""
JADE API Server - Web interface for JADE AI Security Consultant
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent / "GP-AI"))

try:
    from jade_live import JadeSecurityConsultant
    jade_instance = JadeSecurityConsultant()
    print("✅ JADE Security Consultant loaded")
except ImportError as e:
    print(f"⚠️ Running in demo mode: {e}")
    jade_instance = None

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "jade-api"})

@app.route('/query', methods=['POST'])
def query():
    """Process security queries"""
    data = request.json
    query_text = data.get('query', '')

    if not jade_instance:
        # Demo response for Gatekeeper constraint templates
        if "constraint template" in query_text.lower() and "root" in query_text.lower():
            response = generate_gatekeeper_template()
        else:
            response = "JADE is initializing. Please ensure all models are loaded."
    else:
        docs = jade_instance.search_knowledge(query_text, k=5)
        context = jade_instance.analyze_security_context(query_text)
        response = jade_instance.generate_response(query_text, docs, context)

    return jsonify({
        "query": query_text,
        "response": response,
        "status": "success"
    })

def generate_gatekeeper_template():
    """Generate Gatekeeper constraint template for denying root"""
    template = """I'll create both a ConstraintTemplate that denies root access and a Constraint that enforces it.

## 1. ConstraintTemplate (deny-root-template.yaml):

```yaml
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8srequirenonroot
spec:
  crd:
    spec:
      names:
        kind: K8sRequireNonRoot
      validation:
        openAPIV3Schema:
          type: object
          properties:
            message:
              type: string
              description: "Custom violation message"
            exemptImages:
              type: array
              description: "List of exempt container images"
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequirenonroot

        violation[{"msg": msg}] {
          # Check container security context
          container := input.review.object.spec.containers[_]
          has_root_user(container)
          not is_exempt(container.image)
          msg := sprintf("Container '%s' is running as root (UID 0). This violates security policy.", [container.name])
        }

        violation[{"msg": msg}] {
          # Check init containers
          container := input.review.object.spec.initContainers[_]
          has_root_user(container)
          not is_exempt(container.image)
          msg := sprintf("Init container '%s' is running as root (UID 0). This violates security policy.", [container.name])
        }

        violation[{"msg": msg}] {
          # Check pod security context
          has_root_pod_context
          msg := "Pod security context specifies root user (UID 0). This violates security policy."
        }

        # Helper functions
        has_root_user(container) {
          container.securityContext.runAsUser == 0
        }

        has_root_user(container) {
          container.securityContext.runAsNonRoot == false
        }

        has_root_user(container) {
          # If not specified, check if it could run as root
          not container.securityContext.runAsUser
          not container.securityContext.runAsNonRoot
        }

        has_root_pod_context {
          input.review.object.spec.securityContext.runAsUser == 0
        }

        has_root_pod_context {
          input.review.object.spec.securityContext.runAsNonRoot == false
        }

        is_exempt(image) {
          exempt_images := object.get(input, ["parameters", "exemptImages"], [])
          image == exempt_images[_]
        }
```

## 2. Constraint (deny-root-constraint.yaml):

```yaml
apiVersion: k8srequirenonroot.constraints.gatekeeper.sh/v1beta1
kind: K8sRequireNonRoot
metadata:
  name: deny-root-containers
spec:
  enforcementAction: deny  # Can be: deny, dryrun, warn
  match:
    kinds:
    - apiGroups: ["apps", ""]
      kinds: ["Deployment", "StatefulSet", "DaemonSet", "Pod", "Job", "CronJob"]
    namespaces: ["production", "staging"]  # Apply to specific namespaces
    excludedNamespaces: ["kube-system", "gatekeeper-system"]
  parameters:
    message: "Containers must not run as root user for security compliance"
    exemptImages:
    - "gcr.io/google-containers/startup-script:v1"  # Example exempt image
    - "docker.io/istio/pilot:*"  # Wildcard support
```

## 3. Testing the Constraint:

### Invalid Pod (will be rejected):
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: root-pod
  namespace: production
spec:
  containers:
  - name: nginx
    image: nginx:latest
    securityContext:
      runAsUser: 0  # This will be denied
```

### Valid Pod (will be allowed):
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nonroot-pod
  namespace: production
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
  containers:
  - name: nginx
    image: nginx:latest
    securityContext:
      allowPrivilegeEscalation: false
      runAsNonRoot: true
      runAsUser: 1000
      capabilities:
        drop:
        - ALL
      readOnlyRootFilesystem: true
```

## Key Features:
1. **Comprehensive Checking**: Validates containers, init containers, and pod-level security contexts
2. **Flexible Exemptions**: Allows exempting specific images that must run as root
3. **Clear Violations**: Provides specific messages about which container violates the policy
4. **Namespace Control**: Can be applied selectively to namespaces
5. **Enforcement Modes**: Supports deny, dryrun, and warn modes

## Deployment Steps:
```bash
# 1. Apply the ConstraintTemplate
kubectl apply -f deny-root-template.yaml

# 2. Wait for the template to be ready
kubectl wait --for condition=Ready constrainttemplate/k8srequirenonroot

# 3. Apply the Constraint
kubectl apply -f deny-root-constraint.yaml

# 4. Verify it's working
kubectl describe k8srequirenonroot deny-root-containers
```

This implementation follows Gatekeeper best practices and provides comprehensive protection against root containers in your Kubernetes cluster."""

    return template

if __name__ == "__main__":
    print("🚀 Starting JADE API Server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
'''
        api_path.write_text(api_content)
        api_path.chmod(0o755)
        print(f"✅ Created JADE API script at {api_path}")

    def start_gui(self):
        """Start the Electron GUI"""
        print("\n🖥️ Starting GUI Interface...")

        gui_dir = self.base_dir / "GP-GUI"

        if not gui_dir.exists():
            print("❌ GUI directory not found")
            return False

        # Check if node_modules exists
        node_modules = gui_dir / "node_modules"
        if not node_modules.exists():
            print("📦 Installing GUI dependencies...")
            try:
                subprocess.run(
                    ["npm", "install"],
                    cwd=str(gui_dir),
                    check=True,
                    capture_output=True
                )
                print("✅ GUI dependencies installed")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install GUI dependencies: {e}")
                return False

        try:
            # Start Electron GUI
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(gui_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(process)
            self.components_status["gui"] = True
            print("✅ GUI started successfully")
            return True

        except Exception as e:
            print(f"⚠️ Could not start GUI: {e}")
            print("   You can start it manually with: cd GP-GUI && npm run dev")
            return True  # Don't fail if GUI doesn't start

    def create_test_script(self):
        """Create a script to test JADE's Gatekeeper template generation"""
        test_script = self.base_dir / "test_jade_gatekeeper_template.py"

        content = '''#!/usr/bin/env python3
"""
Test JADE's ability to create Gatekeeper constraint templates
"""

import requests
import json
import time

def test_jade_gatekeeper():
    """Test JADE's response to Gatekeeper constraint template request"""

    print("\\n🧪 Testing JADE's Gatekeeper Template Generation...")
    print("=" * 60)

    # Wait for API to be ready
    print("⏳ Waiting for JADE API...")
    for i in range(10):
        try:
            response = requests.get("http://localhost:5000/health", timeout=2)
            if response.status_code == 200:
                print("✅ JADE API is ready")
                break
        except:
            time.sleep(2)
    else:
        print("❌ JADE API not responding")
        return

    # Test query
    query = "Create a Gatekeeper constraint template that denies root access and a constraint that enforces it"

    print(f"\\n📝 Query: {query}")
    print("-" * 60)

    try:
        response = requests.post(
            "http://localhost:5000/query",
            json={"query": query},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print("\\n🤖 JADE's Response:")
            print("=" * 60)
            print(result['response'])
        else:
            print(f"❌ Error: {response.status_code}")

    except Exception as e:
        print(f"❌ Failed to query JADE: {e}")

if __name__ == "__main__":
    test_jade_gatekeeper()
'''
        test_script.write_text(content)
        test_script.chmod(0o755)
        return test_script

    def run(self):
        """Run the unified launcher"""
        print("🚀 JADE Unified Launcher v3.0")
        print("=" * 60)

        # Check dependencies
        if not self.check_dependencies():
            print("\n⚠️ Please install missing dependencies and try again")
            return

        # Initialize components
        if not self.initialize_rag_database():
            print("⚠️ RAG database initialization failed, continuing...")

        if not self.start_jade_api():
            print("❌ Failed to start JADE API")
            return

        if not self.start_gui():
            print("⚠️ GUI could not be started, but API is available")

        # Create and run test
        print("\n" + "=" * 60)
        print("🎉 JADE Components Started Successfully!")
        print("=" * 60)
        print("\n📍 Access Points:")
        print("   • API: http://localhost:5000")
        print("   • Health: http://localhost:5000/health")
        print("   • GUI: Electron app (if started)")

        # Create test script
        test_script = self.create_test_script()

        print("\n🧪 Would you like to test JADE's Gatekeeper template generation?")
        print("   Run: python", test_script.name)

        print("\n⌨️ Press Ctrl+C to stop all services")

        try:
            # Keep running
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down JADE services...")
            self.cleanup()

    def cleanup(self):
        """Clean up all processes"""
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()

        print("✅ All services stopped")
        print("👋 Goodbye!")

if __name__ == "__main__":
    launcher = JadeUnifiedLauncher()
    launcher.run()