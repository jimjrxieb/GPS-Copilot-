# Policies vs Mutators: The Perfect Pairing

**Date:** 2025-10-14
**Purpose:** Explain the relationship between `policies/` (detection) and `mutators/` (correction)

---

## 🎯 The Relationship

### **policies/** = DETECT violations (read-only, validation)
### **mutators/** = CORRECT violations (write, auto-fix)

```
┌─────────────────────────────────────────────────────────────┐
│                    KUBERNETES ADMISSION                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Developer: kubectl apply -f deployment.yaml              │
│                    ↓                                         │
│  2. MUTATING Webhook (mutators/)                            │
│     - Auto-inject security contexts                          │
│     - Add resource limits                                    │
│     - Drop dangerous capabilities                            │
│     - Change :latest → :v1.0.0                              │
│                    ↓                                         │
│  3. VALIDATING Webhook (policies/)                          │
│     - Check if security context exists                       │
│     - Check if resource limits set                           │
│     - Check if capabilities dropped                          │
│     - DENY if violations found                               │
│                    ↓                                         │
│  4. If PASS → Resource created                               │
│     If FAIL → Deployment rejected                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Side-by-Side Comparison

| Aspect | **policies/** (Validator) | **mutators/** (Fixer) |
|--------|---------------------------|------------------------|
| **Purpose** | Detect violations | Correct violations |
| **When** | After mutation, before creation | Before validation |
| **Action** | DENY/ALLOW | MODIFY resource |
| **Type** | Validating Admission Controller | Mutating Admission Controller |
| **OPA Package** | `kubernetes_security`, `terraform_security` | `kubernetes.mutate`, `terraform.mutate` |
| **Output** | `violations[]` array | `patches[]` array (JSONPatch) |
| **Kubernetes** | Gatekeeper Constraints | Gatekeeper Mutations |
| **Terraform** | `conftest test` (blocks apply) | Pre-processing (modifies .tf) |

---

## 🔍 Example: Security Context

### Problem: Developer deploys pod without security context

**Without policies/mutators:**
```yaml
# deployment.yaml (INSECURE)
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  containers:
  - name: app
    image: myapp:latest
    # ❌ No securityContext
    # ❌ No resource limits
    # ❌ Using :latest tag
```

This gets deployed as-is (INSECURE!)

---

### With mutators/ (AUTO-FIX) ✅

**File:** `mutators/opa-policies/kubernetes-mutator.rego`

```rego
package kubernetes.mutate

# MUTATE: Auto-inject security context
mutate_pod_security_context[patch] {
    input.request.kind.kind == "Pod"
    not input.request.object.spec.securityContext  # Missing!

    patch := {
        "op": "add",
        "path": "/spec/securityContext",
        "value": {
            "runAsNonRoot": true,
            "runAsUser": 1000,
            "fsGroup": 2000,
            "seccompProfile": {"type": "RuntimeDefault"}
        }
    }
}

# MUTATE: Add resource limits
mutate_add_resource_limits[patch] {
    container := input.request.object.spec.containers[i]
    not container.resources.limits  # Missing!

    patch := {
        "op": "add",
        "path": sprintf("/spec/containers/%d/resources/limits", [i]),
        "value": {
            "cpu": "500m",
            "memory": "512Mi"
        }
    }
}

# MUTATE: Block :latest tag
mutate_block_latest_tag[patch] {
    container := input.request.object.spec.containers[i]
    endswith(container.image, ":latest")  # Found :latest!

    patch := {
        "op": "replace",
        "path": sprintf("/spec/containers/%d/image", [i]),
        "value": "myapp:v1.0.0"  # Replace with pinned version
    }
}
```

**Result:** Pod is automatically modified BEFORE creation:
```yaml
# After mutators/ auto-fix (SECURE)
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  securityContext:           # ✅ INJECTED by mutator
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:v1.0.0      # ✅ CHANGED from :latest
    resources:
      limits:                 # ✅ INJECTED by mutator
        cpu: 500m
        memory: 512Mi
      requests:
        cpu: 250m
        memory: 256Mi
    securityContext:          # ✅ INJECTED by mutator
      allowPrivilegeEscalation: false
      capabilities:
        drop: [ALL]
      readOnlyRootFilesystem: true
      runAsNonRoot: true
```

---

### With policies/ (VALIDATION) ✅

**File:** `policies/opa/kubernetes.rego`

```rego
package kubernetes_security

# VALIDATE: Security context must exist
violations[{"msg": msg, "severity": "high"}] {
    input.file_type == "config"
    contains(input.file_content, "allowPrivilegeEscalation: true")
    msg := "Privilege escalation is allowed"
}

violations[{"msg": msg, "severity": "medium"}] {
    not input.request.object.spec.securityContext
    msg := "Pod must have securityContext"
}

violations[{"msg": msg, "severity": "medium"}] {
    container := input.request.object.spec.containers[_]
    not container.resources.limits
    msg := "Container must have resource limits"
}
```

**Result:** If mutator didn't fix it, validator BLOCKS deployment:
```
❌ DENIED: Pod must have securityContext
❌ DENIED: Container must have resource limits
```

---

## 🔄 The Complete Workflow

### Step 1: Developer creates insecure YAML
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: insecure-app
spec:
  containers:
  - name: app
    image: myapp:latest
    # Missing everything!
```

### Step 2: Apply to cluster
```bash
kubectl apply -f pod.yaml
```

### Step 3: Mutating Admission Controller (mutators/)
```
🔧 MUTATOR: Analyzing pod...
   ✅ Injecting securityContext
   ✅ Adding resource limits/requests
   ✅ Dropping ALL capabilities
   ✅ Changing :latest → :v1.0.0
   ✅ Setting readOnlyRootFilesystem: true

   Modified YAML sent to next step →
```

### Step 4: Validating Admission Controller (policies/)
```
🔍 VALIDATOR: Checking modified pod...
   ✅ securityContext exists
   ✅ Resource limits set
   ✅ Capabilities dropped
   ✅ No :latest tags
   ✅ Read-only filesystem

   ✅ ALLOWED - Creating pod...
```

### Step 5: Pod created (SECURE!)
```
✅ pod/insecure-app created
   (automatically hardened by mutators)
```

---

## 📁 Directory Mapping

### policies/ (Validators)

```
policies/
├── opa/                           # Conftest validators (pre-deployment)
│   ├── kubernetes.rego            # K8s validation rules
│   ├── terraform-security.rego    # Terraform validation rules
│   ├── pod-security.rego          # Pod Security Standards
│   ├── network-policies.rego      # Network policy enforcement
│   └── secrets-management.rego    # Secrets validation
│
├── gatekeeper/                    # Kubernetes admission validators
│   ├── constraints/               # Active constraints (deployed)
│   └── templates/                 # ConstraintTemplate CRDs
│
└── securebank/                    # PCI-DSS validators
    ├── opa-conftest/              # Terraform validators
    └── opa-gatekeeper/            # K8s validators
```

**Usage:**
```bash
# Terraform validation (conftest)
conftest test tfplan.json --policy policies/opa/

# Kubernetes validation (Gatekeeper)
kubectl apply -f policies/gatekeeper/constraints/
```

---

### mutators/ (Fixers)

```
mutators/
├── opa-policies/                  # OPA mutation rules
│   ├── kubernetes-mutator.rego    # K8s auto-fixes
│   ├── terraform-mutator.rego     # Terraform auto-fixes
│   └── secrets-mutator.rego       # Secrets auto-rotation
│
├── gatekeeper-constraints/        # Gatekeeper mutations
│   └── opa-gatekeeper.yaml        # Mutation config
│
├── webhook-server/                # Custom admission webhook
│   ├── mutating-webhook.py        # Python webhook server
│   ├── Dockerfile                 # Container image
│   └── webhook-config.yaml        # K8s webhook registration
│
├── deploy-gatekeeper.sh           # Install Gatekeeper
└── enable-gatekeeper-enforcement.sh
```

**Usage:**
```bash
# Deploy mutating webhook
cd mutators/webhook-server/
docker build -t mutating-webhook .
kubectl apply -f webhook-config.yaml

# Enable Gatekeeper mutations
cd ../
./deploy-gatekeeper.sh
kubectl apply -f gatekeeper-constraints/opa-gatekeeper.yaml
```

---

## 🎭 Real-World Scenarios

### Scenario 1: :latest Tag

**Without mutators/policies:**
```yaml
image: nginx:latest  # ❌ Gets deployed as-is (BAD!)
```

**With mutators only:**
```rego
# mutators/opa-policies/kubernetes-mutator.rego
mutate_block_latest_tag[patch] {
    endswith(container.image, ":latest")
    patch := {
        "op": "replace",
        "path": "/spec/containers/0/image",
        "value": "nginx:1.25.3"  # Auto-fixed!
    }
}
```
Result: `image: nginx:1.25.3` ✅

**With policies only (no mutator):**
```rego
# policies/opa/image-security.rego
violations[{"msg": msg}] {
    endswith(container.image, ":latest")
    msg := "Image must not use :latest tag"
}
```
Result: Deployment DENIED ❌

**With BOTH (best practice):**
1. Mutator fixes it automatically
2. Validator confirms it was fixed
3. Deployment succeeds ✅

---

### Scenario 2: Privileged Containers

**Developer tries:**
```yaml
securityContext:
  privileged: true  # ❌ Trying to run as root
```

**Mutator response:**
```rego
# mutators/opa-policies/kubernetes-mutator.rego
mutate_disable_privileged[patch] {
    container.securityContext.privileged == true
    patch := {
        "op": "replace",
        "path": "/spec/containers/0/securityContext/privileged",
        "value": false  # Auto-fixed to false
    }
}
```

**Validator confirms:**
```rego
# policies/opa/pod-security.rego
violations[{"msg": msg, "severity": "critical"}] {
    container.securityContext.privileged == true
    msg := "Privileged containers are not allowed"
}
```

**Result:**
- Mutator changes `privileged: true` → `privileged: false`
- Validator checks and passes ✅
- Deployment succeeds (non-privileged) ✅

---

### Scenario 3: Missing Resource Limits

**Developer forgets limits:**
```yaml
containers:
- name: app
  image: myapp:v1.0.0
  # ❌ No resources defined
```

**Mutator injects defaults:**
```rego
# mutators/opa-policies/kubernetes-mutator.rego
mutate_add_resource_limits[patch] {
    not container.resources.limits
    patch := {
        "op": "add",
        "path": "/spec/containers/0/resources/limits",
        "value": {
            "cpu": "500m",
            "memory": "512Mi"
        }
    }
}
```

**Validator confirms:**
```rego
# policies/opa/kubernetes.rego
violations[{"msg": msg}] {
    container := input.request.object.spec.containers[_]
    not container.resources.limits
    msg := "Container must have resource limits"
}
```

**Result:**
- Mutator adds default limits ✅
- Validator passes ✅
- No OOM kills in production ✅

---

## 🔧 How They Work Together

### Phase 1: Security Assessment (Scanning)
**Uses:** `policies/` to DETECT violations

```bash
cd /path/to/GP-CONSULTING/1-Security-Assessment/cd-scanners/
./scan-iac.py /path/to/terraform
# Uses: ../../3-Hardening/policies/opa/terraform-security.rego

./scan-kubernetes.py /path/to/k8s
# Uses: ../../3-Hardening/policies/opa/kubernetes.rego
```

**Output:**
```
❌ Found 15 violations:
   - Pod missing securityContext (HIGH)
   - Container using :latest tag (MEDIUM)
   - No resource limits set (HIGH)
```

---

### Phase 3: Hardening (Enforcement)
**Uses:** `mutators/` to AUTO-FIX violations

```bash
cd /path/to/GP-CONSULTING/3-Hardening/mutators/
./deploy-gatekeeper.sh
kubectl apply -f gatekeeper-constraints/
```

**Result:**
- Future deployments auto-fixed ✅
- Security contexts auto-injected ✅
- Resource limits auto-added ✅
- :latest tags auto-replaced ✅

---

### Deployment (Runtime)
**Uses:** BOTH policies and mutators

```bash
# Developer deploys
kubectl apply -f deployment.yaml

# Behind the scenes:
# 1. Mutating webhook (mutators/) modifies YAML
# 2. Validating webhook (policies/) checks modified YAML
# 3. If pass → created, if fail → denied
```

---

## 📋 Quick Reference

### When to use policies/ (Validators)

✅ **Pre-deployment scanning** (conftest)
```bash
conftest test tfplan.json --policy policies/opa/
```

✅ **Runtime enforcement** (Gatekeeper constraints)
```bash
kubectl apply -f policies/gatekeeper/constraints/
```

✅ **CI/CD gates** (block bad deployments)
```yaml
# .github/workflows/deploy.yml
- name: Validate with OPA
  run: conftest test terraform/ --policy policies/opa/
```

---

### When to use mutators/ (Fixers)

✅ **Auto-fix insecure configurations**
```bash
kubectl apply -f mutators/gatekeeper-constraints/
```

✅ **Developer experience** (don't block, help!)
- Developer forgets securityContext → Auto-injected ✅
- Developer uses :latest → Auto-replaced with pinned version ✅

✅ **Gradual rollout** (mutate first, enforce later)
```bash
# Week 1: Mutate only (auto-fix, allow everything)
kubectl apply -f mutators/

# Week 4: Add validation (start blocking violations)
kubectl apply -f policies/gatekeeper/constraints/
```

---

## 🎯 Best Practice Workflow

### 1. Start with mutators (Week 1-2)
**Why:** Help developers, don't block them

```bash
# Deploy mutating webhooks
cd mutators/
./deploy-gatekeeper.sh
kubectl apply -f gatekeeper-constraints/

# Metrics mode: observe what would be mutated
kubectl get mutations.mutations.gatekeeper.sh
```

**Result:**
- Developers get auto-fixes
- No deployments blocked
- Metrics show what needs fixing

---

### 2. Add validators in audit mode (Week 3-4)
**Why:** Detect violations without blocking

```bash
# Deploy constraints in audit mode
cd ../policies/gatekeeper/constraints/
kubectl apply -f .

# Check violations (doesn't block)
kubectl get constraints
```

**Result:**
- See who has violations
- Give teams time to fix
- No disruption

---

### 3. Enable enforcement (Week 5+)
**Why:** Now everyone is compliant

```bash
# Enable enforcement
kubectl patch constraint pod-security-constraint \
  --type merge \
  -p '{"spec":{"enforcementAction":"deny"}}'
```

**Result:**
- Violations now BLOCKED ✅
- Most deployments already fixed by mutators ✅
- Only new violations blocked ✅

---

## 🔍 Debugging

### Check if mutators are working
```bash
# Deploy a test pod without securityContext
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: test-mutation
spec:
  containers:
  - name: app
    image: nginx:latest
EOF

# Check if securityContext was injected
kubectl get pod test-mutation -o yaml | grep -A 10 securityContext

# Should see auto-injected context:
# securityContext:
#   runAsNonRoot: true
#   runAsUser: 1000
#   ...
```

---

### Check if validators are working
```bash
# Try to deploy privileged pod (should be blocked)
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: privileged-test
spec:
  containers:
  - name: app
    image: nginx
    securityContext:
      privileged: true
EOF

# Should see:
# Error: admission webhook "validation.gatekeeper.sh" denied the request:
# [privileged-containers] Privileged containers are not allowed
```

---

## 📊 Metrics

### Mutation metrics
```bash
# See what's being mutated
kubectl get mutations.mutations.gatekeeper.sh -o yaml

# Count mutations
kubectl get pods -A -o json | \
  jq '[.items[].metadata.annotations |
       select(."mutations.gatekeeper.sh/applied") |
       ."mutations.gatekeeper.sh/applied"] | length'
```

### Validation metrics
```bash
# See violations
kubectl get constraints -A -o json | \
  jq '.items[] | {name: .metadata.name, violations: .status.totalViolations}'

# Check enforcement
kubectl get constraints -A -o json | \
  jq '.items[] | {name: .metadata.name, enforcement: .spec.enforcementAction}'
```

---

## ✅ Summary

| | **policies/** | **mutators/** |
|---|---------------|---------------|
| **Action** | DENY if bad | FIX if bad |
| **When** | After mutation | Before validation |
| **Purpose** | Security gate | Developer experience |
| **Blocks?** | Yes (if enforced) | No (always allows) |
| **Use case** | Compliance, audit | Auto-remediation |
| **Order** | 2nd (validation) | 1st (mutation) |

**Best practice:** Use BOTH for defense-in-depth ✅

---

**Status:** ✅ Production-Ready
**Last Updated:** 2025-10-14
