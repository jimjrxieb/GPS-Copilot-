# Kubernetes OPA Admission Control Policy Primer

## Introduction

This comprehensive guide covers Kubernetes admission control with OPA and how to write effective policies for Kubernetes. This covers the version that uses kube-mgmt. The OPA Gatekeeper version has its own docs.

## Writing Policies

### Basic Policy Structure

To get started, let's look at a common policy: ensure all images come from a trusted registry.

```rego
package kubernetes.admission                                                # line 1
deny contains msg if {                                                      # line 2
    input.request.kind.kind == "Pod"                                        # line 3
    image := input.request.object.spec.containers[_].image                  # line 4
    not startswith(image, "hooli.com/")                                     # line 5
    msg := sprintf("image '%v' comes from untrusted registry", [image])     # line 6
}
```

### Core Concepts

#### Packages
In line 1 the package kubernetes.admission declaration gives the (hierarchical) name kubernetes.admission to the rules in the remainder of the policy. The default installation of OPA as an admission controller assumes your rules are in the package kubernetes.admission.

#### Deny Rules
For admission control, you write deny statements. Order does not matter. In line 2, the head of the rule deny contains msg if says that the admission control request should be rejected and the user handed the error message msg if the conditions in the body are true.

deny is the set of error messages that should be returned to the user. Each rule you write adds to that set of error messages.

#### Input Document Structure

In OPA, input is a reserved, global variable whose value is the Kubernetes AdmissionReview object that the API server hands to any admission control webhook.

Example Pod creation request:
```yaml
kind: Pod
apiVersion: v1
metadata:
  name: myapp
spec:
  containers:
  - image: nginx
    name: nginx-frontend
  - image: mysql
    name: mysql-backend
```

Corresponding AdmissionReview object:
```json
{
  "kind": "AdmissionReview",
  "request": {
    "kind": {
      "kind": "Pod",
      "version": "v1"
    },
    "object": {
      "metadata": {
        "name": "myapp"
      },
      "spec": {
        "containers": [
          {
            "image": "nginx",
            "name": "nginx-frontend"
          },
          {
            "image": "mysql",
            "name": "mysql-backend"
          }
        ]
      }
    }
  }
}
```

### Language Features

#### Dot Notation
The expression `input.request.kind.kind` descends through the YAML hierarchy. The dot (.) operator never throws errors; if the path does not exist the value is undefined.

#### Equality Types
- `x := 7` declares a local variable x and assigns it a value of 7
- `x == 7` returns true if x has a value of 7
- `x = 7` either assigns or compares depending on whether x has a value

#### Array Operations and Iteration
The containers array has an unknown number of elements. To iterate over them, use the anonymous variable `_`:

```rego
image := input.request.object.spec.containers[_].image
```

This finds all images in the containers array and assigns each to the image variable one at a time.

#### Built-in Functions
OPA has 150+ built-ins for analyzing and manipulating:
- Numbers, Strings, Regexes, Networks
- Aggregates, Arrays, Sets
- Types
- Encodings (base64, YAML, JSON, URL, JWT)
- Time

## Testing Policies

Use the OPA unit-test framework before deploying policies:

```rego
package kubernetes.test_admission

import data.kubernetes.admission

test_image_safety if {
  unsafe_image := {
    "request": {
      "kind": {"kind": "Pod"},
      "object": {
        "spec": {
          "containers": [
            {"image": "hooli.com/nginx"},
            {"image": "busybox"}
          ]
        }
      }
    }
  }
  expected := "image 'busybox' comes from untrusted registry"
  admission.deny[expected] with input as unsafe_image
}
```

### Running Tests
```bash
opa test image-safety.rego test-image-safety.rego
# or
opa test .
```

## Using Context in Policies

Sometimes you need to know what other resources exist in the cluster to make policy decisions. For example, preventing conflicting ingresses:

```rego
package kubernetes.admission

deny contains msg if {
  some namespace, name
  input.request.kind.kind == "Ingress"
  newhost := input.request.object.spec.rules[_].host
  oldhost := data.kubernetes.ingresses[namespace][name].spec.rules[_].host
  newhost == oldhost
  input.request.object.metadata.namespace != namespace
  input.request.object.metadata.name != name
  msg := sprintf("ingress host conflicts with ingress %v/%v", [namespace, name])
}
```

### Schema Differences

**input** (AdmissionReview object):
```yaml
apiVersion: admission.k8s.io/v1
kind: AdmissionReview
request:
  kind:
    group: networking.k8s.io
    kind: Ingress
    version: v1
  operation: CREATE
  userInfo:
    groups:
    username: alice
  object:
    metadata:
      name: prod
    spec:
      rules:
      - host: initech.com
```

**data.kubernetes.ingresses[namespace][name]** (Native Kubernetes object):
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: prod
spec:
  rules:
  - host: initech.com
```

## Detailed Admission Control Flow

1. User runs `kubectl create -f pod.yaml`
2. Request reaches API server (authenticated and authorized)
3. Admission controllers process the request
4. Webhook admission controller sends AdmissionReview to OPA
5. OPA evaluates policies and returns AdmissionReview response

### System Main Policy

The system.main policy controls the final admission decision:

```rego
package system

import data.kubernetes.admission

main := {
    "apiVersion": "admission.k8s.io/v1",
    "kind": "AdmissionReview",
    "response": response,
}

default uid := ""

uid := input.request.uid

response := {
    "allowed": false,
    "uid": uid,
    "status": {"message": reason},
} if {
    reason := concat(", ", admission.deny)
    reason != ""
}

else := {"allowed": true, "uid": uid}
```

## Tutorial: Ingress Validation

### Prerequisites
- Kubernetes 1.20 or later
- minikube or KIND for local development

### Step 1: Enable Admission Controllers
```bash
minikube start
minikube addons enable ingress
```

### Step 2: Create Namespace
```bash
kubectl create namespace opa
kubectl config set-context opa-tutorial --user minikube --cluster minikube --namespace opa
kubectl config use-context opa-tutorial
```

### Step 3: Create TLS Credentials
```bash
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -sha256 -key ca.key -days 100000 -out ca.crt -subj "/CN=admission_ca"

cat >server.conf <<EOF
[ req ]
prompt = no
req_extensions = v3_ext
distinguished_name = dn

[ dn ]
CN = opa.opa.svc

[ v3_ext ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth, serverAuth
subjectAltName = DNS:opa.opa.svc,DNS:opa.opa.svc.cluster,DNS:opa.opa.svc.cluster.local
EOF

openssl genrsa -out server.key 2048
openssl req -new -key server.key -sha256 -out server.csr -extensions v3_ext -config server.conf
openssl x509 -req -in server.csr -sha256 -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 100000 -extensions v3_ext -extfile server.conf

kubectl create secret tls opa-server --cert=server.crt --key=server.key --namespace opa
```

### Step 4: Define OPA Policies

#### Policy 1: Restrict Hostnames
```rego
package kubernetes.admission

import data.kubernetes.namespaces

operations := {"CREATE", "UPDATE"}

deny contains msg if {
    input.request.kind.kind == "Ingress"
    operations[input.request.operation]
    host := input.request.object.spec.rules[_].host
    not fqdn_matches_any(host, valid_ingress_hosts)
    msg := sprintf("invalid ingress host %q", [host])
}

valid_ingress_hosts := {host |
    allowlist := namespaces[input.request.namespace].metadata.annotations["ingress-allowlist"]
    hosts := split(allowlist, ",")
    host := hosts[_]
}

fqdn_matches_any(str, patterns) if {
    fqdn_matches(str, patterns[_])
}

fqdn_matches(str, pattern) if {
    pattern_parts := split(pattern, ".")
    pattern_parts[0] == "*"
    suffix := trim(pattern, "*.")
    endswith(str, suffix)
}

fqdn_matches(str, pattern) if {
    not contains(pattern, "*")
    str == pattern
}
```

#### Policy 2: Prohibit Hostname Conflicts
```rego
package kubernetes.admission

import data.kubernetes.ingresses

deny contains msg if {
    some other_ns, other_ingress
    input.request.kind.kind == "Ingress"
    input.request.operation == "CREATE"
    host := input.request.object.spec.rules[_].host
    ingress := ingresses[other_ns][other_ingress]
    other_ns != input.request.namespace
    ingress.spec.rules[_].host == host
    msg := sprintf("invalid ingress host %q (conflicts with %v/%v)", [host, other_ns, other_ingress])
}
```

### Step 5: Build and Publish OPA Bundle
```bash
mkdir policies && cd policies
# Create policy files from above

cat > .manifest <<EOF
{
    "roots": ["kubernetes/admission", "system"]
}
EOF

opa build -b .
docker run --rm --name bundle-server -d -p 8888:80 -v ${PWD}:/usr/share/nginx/html:ro nginx:latest
```

### Step 6: Deploy OPA as Admission Controller

```yaml
# Complete deployment YAML
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: opa-viewer
roleRef:
  kind: ClusterRole
  name: view
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: Group
  name: system:serviceaccounts:opa
  apiGroup: rbac.authorization.k8s.io
---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: opa
  name: configmap-modifier
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["update", "patch"]
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: opa
  name: opa-configmap-modifier
roleRef:
  kind: Role
  name: configmap-modifier
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: Group
  name: system:serviceaccounts:opa
  apiGroup: rbac.authorization.k8s.io
---
kind: Service
apiVersion: v1
metadata:
  name: opa
  namespace: opa
spec:
  selector:
    app: opa
  ports:
  - name: https
    protocol: TCP
    port: 443
    targetPort: 8443
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: opa
  namespace: opa
  name: opa
spec:
  replicas: 1
  selector:
    matchLabels:
      app: opa
  template:
    metadata:
      labels:
        app: opa
      name: opa
    spec:
      containers:
      - name: opa
        image: openpolicyagent/opa:1.9.0
        args:
        - "run"
        - "--server"
        - "--tls-cert-file=/certs/tls.crt"
        - "--tls-private-key-file=/certs/tls.key"
        - "--addr=0.0.0.0:8443"
        - "--addr=http://127.0.0.1:8181"
        - "--set=services.default.url=http://host.minikube.internal:8888"
        - "--set=bundles.default.resource=bundle.tar.gz"
        - "--log-format=json-pretty"
        - "--set=status.console=true"
        - "--set=decision_logs.console=true"
        volumeMounts:
        - readOnly: true
          mountPath: /certs
          name: opa-server
        readinessProbe:
          httpGet:
            path: /health?plugins&bundle
            scheme: HTTPS
            port: 8443
          initialDelaySeconds: 3
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            scheme: HTTPS
            port: 8443
          initialDelaySeconds: 3
          periodSeconds: 5
      - name: kube-mgmt
        image: openpolicyagent/kube-mgmt:9.0.1
        args:
        - "--replicate-cluster=v1/namespaces"
        - "--replicate=networking.k8s.io/v1/ingresses"
      volumes:
      - name: opa-server
        secret:
          secretName: opa-server
```

### Step 7: Register Webhook
```bash
cat > webhook-configuration.yaml <<EOF
kind: ValidatingWebhookConfiguration
apiVersion: admissionregistration.k8s.io/v1
metadata:
  name: opa-validating-webhook
webhooks:
  - name: validating-webhook.openpolicyagent.org
    namespaceSelector:
      matchExpressions:
      - key: openpolicyagent.org/webhook
        operator: NotIn
        values:
        - ignore
    rules:
      - operations: ["CREATE", "UPDATE"]
        apiGroups: ["*"]
        apiVersions: ["*"]
        resources: ["*"]
    clientConfig:
      caBundle: $(cat ca.crt | base64 | tr -d '\n')
      service:
        namespace: opa
        name: opa
    admissionReviewVersions: ["v1"]
    sideEffects: None
EOF

kubectl label ns kube-system openpolicyagent.org/webhook=ignore
kubectl label ns opa openpolicyagent.org/webhook=ignore
kubectl apply -f webhook-configuration.yaml
```

### Step 8: Test Policies

Create test namespaces:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  annotations:
    ingress-allowlist: "*.qa.acmecorp.com,*.internal.acmecorp.com"
  name: qa
---
apiVersion: v1
kind: Namespace
metadata:
  annotations:
    ingress-allowlist: "*.acmecorp.com"
  name: production
```

Test ingress creation:
```yaml
# This will succeed
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-ok
spec:
  rules:
  - host: signin.acmecorp.com
    http:
      paths:
      - pathType: ImplementationSpecific
        path: /
        backend:
          service:
            name: nginx
            port:
              number: 80
```

```yaml
# This will fail
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-bad
spec:
  rules:
  - host: acmecorp.com
    http:
      paths:
      - pathType: ImplementationSpecific
        path: /
        backend:
          service:
            name: nginx
            port:
              number: 80
```

## Debugging Tips

### Check Policy Status
Look for the `openpolicyagent.org/kube-mgmt-status` annotation on ConfigMaps containing policies. Should show `{"status":"ok"}` if loaded successfully.

### Check Container Logs
- **kube-mgmt**: Should be quiet when healthy
- **opa**: Look for TLS errors and POST requests

### Verify Webhook Configuration
Ensure proper namespace labeling and webhook scope.

### Mutating Policy Requirements
For mutating policies:
1. Escape "/" characters in JSON Pointer using `~1`
2. Use `base64.encode()` (not `base64url.encode()`)

Example correct mutating policy:
```rego
response := {
  "allowed": true,
  "patchType": "JSONPatch",
  "patch": base64.encode(json.marshal(patches))
}

patches := [
  {
    "op": "add",
    "path": "/metadata/annotations/acmecorp.com~1myannotation",
    "value": "somevalue"
  }
]
```

## Integration with GP-Copilot Security Framework

### Policy Categories for Automated Analysis

When GP-Copilot encounters Kubernetes admission control policies, Jade should categorize them:

#### Security Policies
- Image registry restrictions
- Security context enforcement
- Network policy validation
- Secret and ConfigMap access controls

#### Compliance Policies
- Resource labeling requirements
- Namespace isolation rules
- Audit logging enforcement
- Data classification validation

#### Operational Policies
- Resource quotas and limits
- Naming convention enforcement
- Deployment patterns validation
- Service mesh configuration

### Automated Policy Generation

Jade should be able to generate OPA policies for common security scenarios:

1. **Image Security**: Registry allowlists, vulnerability scanning requirements
2. **RBAC Enforcement**: Service account restrictions, privilege escalation prevention
3. **Network Security**: Ingress/egress controls, service mesh requirements
4. **Data Protection**: Encryption requirements, secret management validation

### Policy Testing Framework Integration

For each generated policy, Jade should provide:
- Unit tests with positive and negative test cases
- Integration test scenarios
- Performance impact assessments
- Rollback procedures

This comprehensive primer enables Jade to provide expert-level guidance on Kubernetes admission control with OPA, from basic policy writing to complex enterprise deployments.