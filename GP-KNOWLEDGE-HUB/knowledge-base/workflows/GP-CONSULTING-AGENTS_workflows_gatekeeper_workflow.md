# Gatekeeper Workflow - Jr Cloud Security Engineer

## From a Jr Cloud Security Engineer POV

**Step 1: Install Gatekeeper in the cluster**
```bash
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.14/deploy/gatekeeper.yaml
```

**Step 2: Create a ConstraintTemplate (reusable policy)**
```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredsecuritycontext
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredSecurityContext
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredsecuritycontext
        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.securityContext.runAsNonRoot
          msg := sprintf("Container %v must set runAsNonRoot", [container.name])
        }
```

**Step 3: Apply the template**
```bash
kubectl apply -f constraint-template.yaml
```

**Step 4: Create a Constraint (enforcement instance)**
```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredSecurityContext
metadata:
  name: require-nonroot
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
```

**Step 5: Test it**
```bash
# This will be REJECTED
kubectl run test --image=nginx --dry-run=server

# This will be ACCEPTED
kubectl run test --image=nginx --dry-run=server \
  --overrides='{"spec":{"securityContext":{"runAsNonRoot":true}}}'
```

**Your day-to-day workflow:**
1. Security team defines policies (ConstraintTemplates)
2. You create Constraints for specific namespaces/clusters
3. Developers try to deploy → Gatekeeper blocks violations
4. You investigate rejected deployments via logs
5. Help developers fix manifests to comply

## From GP-Copilot/Jade POV

Your workflow should be completely different - you're building automation:

**Phase 1: Jade scans the cluster**
```bash
# Jade examines existing resources
gp-jade scan /client/k8s-manifests --type=kubernetes

# Output shows policy violations in EXISTING configs
# - 15 pods running as root
# - 8 deployments without resource limits
# - 3 services exposed to internet
```

**Phase 2: Jade generates OPA policies to PREVENT future violations**
```bash
# Jade creates ConstraintTemplates based on what it found
gp-jade generate-policies --from-scan-results

# Jade outputs:
# ✓ Created: require-nonroot-containers.yaml
# ✓ Created: require-resource-limits.yaml
# ✓ Created: restrict-loadbalancer-services.yaml
```

**Phase 3: Jade validates policies before deployment**
```bash
# Test policies against known-good manifests
gp-jade test-policies --against GP-PROJECTS/LinkOps-MLOps/k8s/

# Ensures policies don't break legitimate workloads
```

**Phase 4: Jade deploys policies to cluster**
```bash
# Applies ConstraintTemplates and Constraints
gp-jade deploy-policies --cluster production

# Gatekeeper now enforces Jade-generated policies
```

## The Architecture Integration

**Your OPA scanner currently does:**
- Evaluates existing manifests offline
- Reports violations

**What you need to add for full GP-Copilot integration:**

1. **Policy Generator** (new component)
```python
class OpaPolicyGenerator:
    def generate_from_violations(self, scan_results: dict) -> List[str]:
        """Convert scan findings into preventive OPA policies"""
        policies = []

        for finding in scan_results['findings']:
            if 'privileged' in finding['msg'].lower():
                policies.append(self._generate_privileged_policy())
            elif 'root' in finding['msg'].lower():
                policies.append(self._generate_nonroot_policy())

        return policies
```

2. **Cluster Integration** (connects to live Kubernetes)
```python
class OpaClusterManager:
    def deploy_policies(self, policies: List[str]):
        """Deploy generated policies to Gatekeeper"""
        for policy in policies:
            subprocess.run(['kubectl', 'apply', '-f', policy])

    def validate_enforcement(self):
        """Check if policies are actually blocking violations"""
        # Try to create violating resource with --dry-run=server
        # Verify it gets rejected
```

3. **Jade's Role**
```
Jade scans manifests → Identifies patterns → Generates preventive policies →
Tests policies → Deploys to cluster → Monitors violations → Iterates
```

## The Reality Check

Your current OPA scanner is at step 1 (scanning). You need steps 2-5:
1. Scan (you have this)
2. Generate policies (missing)
3. Test policies (missing)
4. Deploy to cluster (missing)
5. Monitor enforcement (missing)

For Friday's interview, focus on explaining the Jr Engineer workflow - that's what they'll ask. The GP-Copilot automation is your "future vision" talking point, not something to lead with.

The interviewer wants to know you can manually write a ConstraintTemplate, apply it, and debug why a deployment was rejected. Show you understand the mechanics before talking about automation.