# Kubernetes Admission Control Flow

**policies/** (Validators) + **mutators/** (Fixers) = Complete Security

---

## 🔄 Complete Admission Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DEVELOPER WORKFLOW                               │
└─────────────────────────────────────────────────────────────────────────┘

1. Developer creates YAML (potentially insecure):
   ─────────────────────────────────────────────
   apiVersion: v1
   kind: Pod
   metadata:
     name: myapp
   spec:
     containers:
     - name: app
       image: nginx:latest              ❌ :latest tag
       # No securityContext             ❌ Missing
       # No resource limits              ❌ Missing


2. Developer applies:
   ─────────────────────────────────────────────
   $ kubectl apply -f pod.yaml

   ↓


┌─────────────────────────────────────────────────────────────────────────┐
│                      KUBERNETES API SERVER                               │
└─────────────────────────────────────────────────────────────────────────┘

3. API Server receives request
   ─────────────────────────────────────────────
   Request: Create Pod "myapp"

   ↓


┌─────────────────────────────────────────────────────────────────────────┐
│           STEP 1: MUTATING ADMISSION WEBHOOKS                            │
│           (mutators/ directory)                                          │
└─────────────────────────────────────────────────────────────────────────┘

4. Mutating Webhook #1: OPA Gatekeeper Mutate
   ─────────────────────────────────────────────
   File: mutators/opa-policies/kubernetes-mutator.rego

   🔧 Mutation 1: Inject securityContext
      Operation: ADD
      Path: /spec/securityContext
      Value: {
        runAsNonRoot: true,
        runAsUser: 1000,
        fsGroup: 2000
      }

   🔧 Mutation 2: Inject container securityContext
      Operation: ADD
      Path: /spec/containers/0/securityContext
      Value: {
        allowPrivilegeEscalation: false,
        capabilities: { drop: ["ALL"] },
        readOnlyRootFilesystem: true
      }

   🔧 Mutation 3: Add resource limits
      Operation: ADD
      Path: /spec/containers/0/resources/limits
      Value: {
        cpu: "500m",
        memory: "512Mi"
      }

   🔧 Mutation 4: Replace :latest tag
      Operation: REPLACE
      Path: /spec/containers/0/image
      Value: "nginx:1.25.3"

   ✅ Mutations applied: 4

   ↓


5. Modified YAML (after mutations):
   ─────────────────────────────────────────────
   apiVersion: v1
   kind: Pod
   metadata:
     name: myapp
   spec:
     securityContext:                   ✅ INJECTED
       runAsNonRoot: true
       runAsUser: 1000
       fsGroup: 2000
     containers:
     - name: app
       image: nginx:1.25.3              ✅ FIXED (:latest → :1.25.3)
       resources:                        ✅ INJECTED
         limits:
           cpu: 500m
           memory: 512Mi
         requests:
           cpu: 250m
           memory: 256Mi
       securityContext:                  ✅ INJECTED
         allowPrivilegeEscalation: false
         capabilities:
           drop: [ALL]
         readOnlyRootFilesystem: true
         runAsNonRoot: true

   ↓


┌─────────────────────────────────────────────────────────────────────────┐
│           STEP 2: VALIDATING ADMISSION WEBHOOKS                          │
│           (policies/ directory)                                          │
└─────────────────────────────────────────────────────────────────────────┘

6. Validating Webhook #1: OPA Gatekeeper Validate
   ─────────────────────────────────────────────
   File: policies/opa/kubernetes.rego

   🔍 Check 1: securityContext exists?
      ✅ PASS - Found at /spec/securityContext

   🔍 Check 2: No privilege escalation?
      ✅ PASS - allowPrivilegeEscalation: false

   🔍 Check 3: Resource limits set?
      ✅ PASS - Found cpu/memory limits

   🔍 Check 4: No :latest tags?
      ✅ PASS - Image is nginx:1.25.3

   🔍 Check 5: Capabilities dropped?
      ✅ PASS - ALL capabilities dropped

   ✅ All validation checks passed

   ↓


7. Validating Webhook #2: Pod Security Standards
   ─────────────────────────────────────────────
   File: policies/gatekeeper/constraints/pod-security-constraint.yaml

   🔍 Check: Meets "restricted" Pod Security Standard?
      ✅ PASS - All requirements met

   ↓


┌─────────────────────────────────────────────────────────────────────────┐
│                      ADMISSION DECISION                                  │
└─────────────────────────────────────────────────────────────────────────┘

8. Decision: ALLOW ✅
   ─────────────────────────────────────────────
   Reason: All mutations applied, all validations passed

   ↓


┌─────────────────────────────────────────────────────────────────────────┐
│                      RESOURCE CREATION                                   │
└─────────────────────────────────────────────────────────────────────────┘

9. Pod created in cluster (SECURE!)
   ─────────────────────────────────────────────
   $ kubectl get pods
   NAME    READY   STATUS    RESTARTS   AGE
   myapp   1/1     Running   0          5s

   $ kubectl describe pod myapp
   ...
   Security Context:               ✅ Auto-injected by mutator
     Run As User: 1000
     Run As Non-Root: true
     Read Only Root Filesystem: true
     Capabilities:
       Drop: ALL
   Resource Limits:                ✅ Auto-injected by mutator
     cpu: 500m
     memory: 512Mi

   ✅ Pod is production-ready and secure!


┌─────────────────────────────────────────────────────────────────────────┐
│                      DEVELOPER EXPERIENCE                                │
└─────────────────────────────────────────────────────────────────────────┘

10. Developer sees:
   ─────────────────────────────────────────────
   ✅ Deployment succeeded
   ✅ No errors or rejections
   ✅ Pod is automatically hardened

   Developer didn't need to:
   - Know about securityContext
   - Remember resource limits
   - Pin image tags
   - Drop capabilities

   Mutators handled it all automatically! 🎉
```

---

## ❌ Alternative Flow: Without Mutators (Policies Only)

```
1. Developer creates YAML (insecure):
   ─────────────────────────────────────────────
   apiVersion: v1
   kind: Pod
   spec:
     containers:
     - name: app
       image: nginx:latest
       # No securityContext
       # No resource limits


2. Developer applies:
   ─────────────────────────────────────────────
   $ kubectl apply -f pod.yaml

   ↓


3. No mutations (no mutators configured)
   ─────────────────────────────────────────────
   YAML unchanged

   ↓


4. Validating Webhook (policies only):
   ─────────────────────────────────────────────
   🔍 Check: securityContext exists?
      ❌ FAIL - Not found

   🔍 Check: Resource limits set?
      ❌ FAIL - Not found

   🔍 Check: No :latest tags?
      ❌ FAIL - Found :latest

   ↓


5. Decision: DENY ❌
   ─────────────────────────────────────────────
   Error from server (Forbidden): error when creating "pod.yaml":
   admission webhook "validation.gatekeeper.sh" denied the request:
   [pod-security-context] Pod must have securityContext
   [resource-limits-required] Containers must have resource limits
   [no-latest-tags] Image tags must not use :latest

   ↓


6. Developer experience:
   ─────────────────────────────────────────────
   ❌ Deployment BLOCKED
   😞 Developer frustrated
   ❓ Developer doesn't know what securityContext is
   ⏰ Developer spends 2 hours Googling

   Bad experience!
```

---

## ✅ Best Practice: Mutators THEN Validators

```
┌──────────────────────────────────────────────────────────────┐
│                    DEFENSE IN DEPTH                           │
└──────────────────────────────────────────────────────────────┘

Layer 1: MUTATORS (mutators/)
  ✅ Auto-fix common issues
  ✅ Improve developer experience
  ✅ Reduce blocked deployments
  ✅ Gradual enforcement

Layer 2: VALIDATORS (policies/)
  ✅ Enforce security policies
  ✅ Catch what mutators missed
  ✅ Compliance enforcement
  ✅ Audit trail

Result:
  ✅ 95% of deployments auto-fixed by mutators
  ✅ Only 5% blocked by validators (truly bad configs)
  ✅ Happy developers + secure cluster
```

---

## 🎯 Real-World Example: Rollout Strategy

### Week 1-2: Mutators Only (Learning Mode)
```bash
# Deploy mutating webhooks
cd mutators/
./deploy-gatekeeper.sh
kubectl apply -f gatekeeper-constraints/

# Observe what would be mutated
kubectl get mutations.mutations.gatekeeper.sh -o json | \
  jq '.items[].status.mutationCount'

# Example output:
# {
#   "securityContext_injected": 145,
#   "resource_limits_added": 89,
#   "latest_tags_replaced": 67,
#   "capabilities_dropped": 145
# }
```

**Result:**
- ✅ 145 pods auto-fixed with securityContext
- ✅ 89 pods auto-fixed with resource limits
- ✅ 67 images changed from :latest
- ❌ 0 deployments blocked
- 😊 Developers happy

---

### Week 3-4: Add Validators in Audit Mode
```bash
# Deploy constraints in audit mode (don't block)
cd ../policies/gatekeeper/constraints/
kubectl apply -f - <<EOF
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequireSecurityContext
metadata:
  name: pod-security-context
spec:
  enforcementAction: "dryrun"  # Audit only, don't block
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Pod"]
EOF

# Check violations (doesn't block)
kubectl get constraints -o json | \
  jq '.items[].status.violations'

# Example output:
# [
#   {
#     "kind": "Pod",
#     "name": "legacy-app",
#     "message": "Pod missing securityContext (would be blocked if enforced)"
#   }
# ]
```

**Result:**
- ✅ See what would be blocked
- ✅ Give teams time to fix
- ❌ 0 deployments blocked
- 📊 Metrics collected

---

### Week 5+: Enable Enforcement
```bash
# Enable enforcement (now block violations)
kubectl patch constraint pod-security-context \
  --type merge \
  -p '{"spec":{"enforcementAction":"deny"}}'

# Now violations are BLOCKED
kubectl apply -f bad-pod.yaml
# Error: admission webhook denied the request
```

**Result:**
- ✅ Most deployments already fixed by mutators (weeks 1-4)
- ✅ Only truly bad configs blocked
- ✅ Secure cluster
- 😊 Developers had time to learn

---

## 📊 Monitoring

### Mutation Metrics
```bash
# How many resources mutated today?
kubectl get mutations.mutations.gatekeeper.sh -o json | \
  jq '.items[] | {
    name: .metadata.name,
    mutations_applied: .status.mutationCount,
    last_mutation: .status.lastMutation
  }'
```

### Validation Metrics
```bash
# How many violations detected?
kubectl get constraints -o json | \
  jq '.items[] | {
    constraint: .metadata.name,
    total_violations: .status.totalViolations,
    enforcement: .spec.enforcementAction
  }'
```

### Alerting
```bash
# Alert if violations increase
kubectl get constraints -o json | \
  jq '.items[] | select(.status.totalViolations > 10) | {
    alert: "High violation count",
    constraint: .metadata.name,
    violations: .status.totalViolations
  }'
```

---

## 🔧 Debugging

### Check if mutations are applied
```bash
# Deploy test pod
kubectl run test --image=nginx:latest --dry-run=server -o yaml

# Should see mutations in annotations:
# metadata:
#   annotations:
#     mutations.gatekeeper.sh/applied: "4"
#     mutations.gatekeeper.sh/list: "inject-security-context,add-resource-limits,..."
```

### Check validation results
```bash
# Try deploying a privileged pod
kubectl run privileged --image=nginx --privileged=true

# Should see denial:
# Error from server (Forbidden): pods "privileged" is forbidden:
# [privileged-containers] Privileged containers are not allowed
```

---

## 📋 Summary

| Phase | Mutators | Validators | Deployments Blocked | Developer Experience |
|-------|----------|------------|---------------------|---------------------|
| **Week 1-2** | ✅ Enabled | ❌ Disabled | 0% | 😊 Great (auto-fixes) |
| **Week 3-4** | ✅ Enabled | 🟡 Audit mode | 0% | 😊 Great (warnings) |
| **Week 5+** | ✅ Enabled | ✅ Enforced | ~5% | 😊 Good (already compliant) |
| **No mutators** | ❌ Disabled | ✅ Enforced | ~80% | 😞 Poor (constant blocks) |

**Best practice:** Mutators + Validators = Happy developers + Secure cluster ✅

---

**File:** [ADMISSION-CONTROL-FLOW.md](ADMISSION-CONTROL-FLOW.md)
**Last Updated:** 2025-10-14
**Status:** ✅ Production-Ready
