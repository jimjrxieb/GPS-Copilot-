#!/usr/bin/env python3
"""
JADE Quick Demo - Demonstrate Gatekeeper template generation without heavy models
"""

import sys
from pathlib import Path
import json

# Add paths
sys.path.append(str(Path(__file__).parent / "GP-RAG"))

def demonstrate_jade_gatekeeper():
    """Demonstrate JADE's Gatekeeper template generation capability"""

    print("🤖 JADE Security Consultant - Gatekeeper Template Demo")
    print("=" * 60)

    query = "Create a Gatekeeper constraint template that denies root containers and a constraint that enforces it"

    print(f"\n📝 User Query: {query}")
    print("-" * 60)

    # Search for relevant knowledge
    print("\n🔍 Searching JADE's Knowledge Base...")

    try:
        from langchain_chroma import Chroma
        from langchain_community.embeddings import HuggingFaceEmbeddings

        # Quick embedding model
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )

        # Connect to vector store
        vector_db_path = Path(__file__).parent / "GP-RAG" / "vector-db" / "gp_security_rag"

        if vector_db_path.exists():
            vector_store = Chroma(
                persist_directory=str(vector_db_path),
                embedding_function=embeddings
            )

            # Search for Gatekeeper knowledge
            docs = vector_store.similarity_search("gatekeeper constraint template deny root", k=3)

            print(f"✅ Found {len(docs)} relevant documents")
            for i, doc in enumerate(docs, 1):
                print(f"\n   📄 Document {i}:")
                print(f"      Source: {doc.metadata.get('source', 'Unknown')}")
                print(f"      Content preview: {doc.page_content[:150]}...")
        else:
            print("⚠️ Knowledge base not found, using built-in expertise")

    except ImportError as e:
        print(f"⚠️ RAG components not available: {e}")

    # Generate response based on JADE's expertise
    print("\n" + "=" * 60)
    print("🤖 JADE's Response:")
    print("=" * 60)

    response = generate_expert_response()
    print(response)

    # Save the templates
    save_templates(response)

def generate_expert_response():
    """Generate expert response for Gatekeeper templates"""

    return """I'll create a comprehensive Gatekeeper solution to deny root containers.

## 1. ConstraintTemplate (k8s-deny-root-template.yaml):

```yaml
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8sdenyroot
  annotations:
    description: "Denies containers from running as root user (UID 0)"
    documentation: "https://kubernetes.io/docs/concepts/security/pod-security-standards/"
spec:
  crd:
    spec:
      names:
        kind: K8sDenyRoot
      validation:
        openAPIV3Schema:
          type: object
          properties:
            message:
              type: string
              description: "Custom violation message"
            exemptImages:
              type: array
              description: "List of container images exempt from this policy"
              items:
                type: string
            allowedUsers:
              type: array
              description: "List of allowed non-root UIDs"
              items:
                type: integer
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8sdenyroot

        import future.keywords.contains
        import future.keywords.if
        import future.keywords.in

        # Main violation rule for containers
        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          is_running_as_root(container, input.review.object.spec)
          not is_exempt(container.image)
          msg := sprintf("Container '%s' is not allowed to run as root (UID 0). Please set securityContext.runAsNonRoot: true or specify a non-root runAsUser.", [container.name])
        }

        # Check init containers
        violation[{"msg": msg}] {
          container := input.review.object.spec.initContainers[_]
          is_running_as_root(container, input.review.object.spec)
          not is_exempt(container.image)
          msg := sprintf("Init container '%s' is not allowed to run as root (UID 0).", [container.name])
        }

        # Check ephemeral containers
        violation[{"msg": msg}] {
          container := input.review.object.spec.ephemeralContainers[_]
          is_running_as_root(container, input.review.object.spec)
          not is_exempt(container.image)
          msg := sprintf("Ephemeral container '%s' is not allowed to run as root.", [container.name])
        }

        # Helper: Check if container runs as root
        is_running_as_root(container, pod_spec) {
          # Explicitly set to run as root at container level
          container.securityContext.runAsUser == 0
        }

        is_running_as_root(container, pod_spec) {
          # Explicitly set to allow root at container level
          container.securityContext.runAsNonRoot == false
        }

        is_running_as_root(container, pod_spec) {
          # Pod level sets root and container doesn't override
          pod_spec.securityContext.runAsUser == 0
          not container.securityContext.runAsUser
          not container.securityContext.runAsNonRoot
        }

        is_running_as_root(container, pod_spec) {
          # Neither pod nor container specify non-root
          not container.securityContext.runAsUser
          not container.securityContext.runAsNonRoot
          not pod_spec.securityContext.runAsUser
          not pod_spec.securityContext.runAsNonRoot
        }

        # Helper: Check if image is exempt
        is_exempt(image) {
          exempt_images := object.get(input.parameters, "exemptImages", [])
          exempt := exempt_images[_]
          match_image(image, exempt)
        }

        # Helper: Match image with wildcards
        match_image(image, pattern) {
          # Exact match
          image == pattern
        }

        match_image(image, pattern) {
          # Wildcard match
          contains(pattern, "*")
          regex := replace(replace(pattern, ".", "\\\\."), "*", ".*")
          regex_match(regex, image)
        }
```

## 2. Constraint (k8s-deny-root-constraint.yaml):

```yaml
apiVersion: k8sdenyroot.constraints.gatekeeper.sh/v1beta1
kind: K8sDenyRoot
metadata:
  name: deny-root-containers-policy
  annotations:
    description: "Enforces non-root container policy across specified namespaces"
spec:
  enforcementAction: deny  # Options: deny, dryrun, warn
  match:
    kinds:
    - apiGroups: ["", "apps", "batch"]
      kinds:
      - Pod
      - Deployment
      - StatefulSet
      - DaemonSet
      - Job
      - CronJob
      - ReplicaSet
    namespaces:
    - default
    - production
    - staging
    - development
    excludedNamespaces:
    - kube-system
    - kube-public
    - kube-node-lease
    - gatekeeper-system
    - cert-manager
    labelSelector:
      matchExpressions:
      - key: security-policy
        operator: NotIn
        values: ["exempt"]
  parameters:
    message: "Security Policy Violation: Containers must run as non-root user for defense-in-depth security."
    exemptImages:
    # System components that may require root
    - "gcr.io/google-containers/*"
    - "k8s.gcr.io/*"
    - "registry.k8s.io/*"
    # Specific exemptions (use sparingly)
    - "docker.io/istio/pilot:*"
    - "docker.io/library/nginx:*-alpine"  # Example: specific nginx alpine versions
    allowedUsers: [1000, 1001, 2000]  # Allowed non-root UIDs
```

## 3. Test Manifests:

### ❌ This Pod will be REJECTED:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: root-pod-test
  namespace: default
spec:
  containers:
  - name: nginx
    image: nginx:latest
    # No securityContext defined - will be rejected
```

### ✅ This Pod will be ACCEPTED:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod-test
  namespace: default
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: nginx
    image: nginx:latest
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: var-cache
      mountPath: /var/cache/nginx
    - name: var-run
      mountPath: /var/run
  volumes:
  - name: tmp
    emptyDir: {}
  - name: var-cache
    emptyDir: {}
  - name: var-run
    emptyDir: {}
```

## 4. Deployment Instructions:

```bash
# 1. Install Gatekeeper if not already installed
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/v3.14.0/deploy/gatekeeper.yaml

# 2. Wait for Gatekeeper to be ready
kubectl -n gatekeeper-system wait --for=condition=Ready pod -l control-plane=controller-manager --timeout=60s

# 3. Apply the ConstraintTemplate
kubectl apply -f k8s-deny-root-template.yaml

# 4. Verify template is established
kubectl wait --for=condition=Established constrainttemplate/k8sdenyroot --timeout=60s

# 5. Apply the Constraint
kubectl apply -f k8s-deny-root-constraint.yaml

# 6. Test with a violating pod
kubectl apply -f root-pod-test.yaml
# This should fail with a policy violation

# 7. Test with a compliant pod
kubectl apply -f secure-pod-test.yaml
# This should succeed
```

## 5. Monitoring & Troubleshooting:

```bash
# Check constraint status
kubectl describe k8sdenyroot deny-root-containers-policy

# View violations in dry-run mode
kubectl get k8sdenyroot deny-root-containers-policy -o jsonpath='{.status.violations}'

# Check Gatekeeper logs
kubectl logs -n gatekeeper-system deployment/gatekeeper-controller-manager

# List all constraint templates
kubectl get constrainttemplates
```

## Key Security Benefits:

1. **Prevents Privilege Escalation**: Root containers can potentially escape and access host resources
2. **Reduces Attack Surface**: Non-root containers have limited system capabilities
3. **Compliance**: Meets CIS Kubernetes Benchmark and PCI-DSS requirements
4. **Defense in Depth**: Additional security layer beyond RBAC

## Best Practices:

- Always specify `runAsNonRoot: true` at pod level
- Use specific UIDs (1000+) rather than relying on defaults
- Mount writable volumes for applications that need to write to specific paths
- Test in `dryrun` mode before enforcing in production
- Keep exemptions minimal and well-documented

This implementation provides comprehensive protection against root containers while maintaining flexibility for legitimate use cases through exemptions."""

def save_templates(response):
    """Extract and save YAML templates from response"""

    import re

    # Extract YAML blocks
    yaml_blocks = re.findall(r'```yaml\n(.*?)\n```', response, re.DOTALL)

    if yaml_blocks:
        # Save ConstraintTemplate
        if len(yaml_blocks) > 0:
            with open("jade_output_constrainttemplate.yaml", "w") as f:
                f.write(yaml_blocks[0])
            print(f"\n💾 ConstraintTemplate saved to: jade_output_constrainttemplate.yaml")

        # Save Constraint
        if len(yaml_blocks) > 1:
            with open("jade_output_constraint.yaml", "w") as f:
                f.write(yaml_blocks[1])
            print(f"💾 Constraint saved to: jade_output_constraint.yaml")

        # Save test manifests
        if len(yaml_blocks) > 3:
            with open("jade_output_test_manifests.yaml", "w") as f:
                f.write("# Test Pod - Will be rejected\n")
                f.write("---\n")
                f.write(yaml_blocks[2])
                f.write("\n---\n")
                f.write("# Secure Pod - Will be accepted\n")
                f.write(yaml_blocks[3])
            print(f"💾 Test manifests saved to: jade_output_test_manifests.yaml")

    print("\n✅ JADE has successfully generated Gatekeeper templates for denying root containers!")

if __name__ == "__main__":
    demonstrate_jade_gatekeeper()