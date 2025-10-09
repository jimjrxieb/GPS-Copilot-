#!/bin/bash
set -e

echo "🔧 Auto-Fixer: Kubernetes Security Violations"
echo "═══════════════════════════════════════════════"

K8S_DIR="../../../../infrastructure/k8s"

echo ""
echo "→ Injecting pod security context..."

# Fix deployment.yaml
if [ -f "$K8S_DIR/deployment.yaml" ]; then
  # Add pod security context if not present
  if ! grep -q "runAsNonRoot" "$K8S_DIR/deployment.yaml"; then
    sed -i '/spec:/a \      securityContext:\n        runAsNonRoot: true\n        runAsUser: 1000\n        fsGroup: 2000' "$K8S_DIR/deployment.yaml"
  fi

  # Add container security context if not present
  if ! grep -q "allowPrivilegeEscalation" "$K8S_DIR/deployment.yaml"; then
    sed -i '/containers:/,/image:/ {
      /image:/a \          securityContext:\n            allowPrivilegeEscalation: false\n            capabilities:\n              drop:\n                - ALL\n            readOnlyRootFilesystem: true\n            runAsNonRoot: true
    }' "$K8S_DIR/deployment.yaml"
  fi

  echo "✅ Pod security context injected"
else
  echo "⚠️  deployment.yaml not found"
fi

echo ""
echo "→ Disabling privileged containers..."
sed -i 's/privileged:[[:space:]]*true/privileged: false/g' "$K8S_DIR"/*.yaml
echo "✅ Privileged containers disabled"

echo ""
echo "→ Disabling hostNetwork..."
sed -i 's/hostNetwork:[[:space:]]*true/hostNetwork: false/g' "$K8S_DIR"/*.yaml
echo "✅ hostNetwork disabled"

echo ""
echo "→ Disabling hostPID..."
sed -i 's/hostPID:[[:space:]]*true/hostPID: false/g' "$K8S_DIR"/*.yaml
echo "✅ hostPID disabled"

echo ""
echo "→ Adding resource limits..."
if ! grep -q "resources:" "$K8S_DIR/deployment.yaml"; then
  sed -i '/image:/a \          resources:\n            limits:\n              cpu: 500m\n              memory: 512Mi\n            requests:\n              cpu: 250m\n              memory: 256Mi' "$K8S_DIR/deployment.yaml"
fi
echo "✅ Resource limits added"

echo ""
echo "→ Creating network policy..."
cat > "$K8S_DIR/network-policy.yaml" << 'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: securebank-network-policy
  namespace: securebank
spec:
  podSelector:
    matchLabels:
      app: securebank
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: securebank
      ports:
        - protocol: TCP
          port: 3000
        - protocol: TCP
          port: 5000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - protocol: TCP
          port: 6379
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: TCP
          port: 53
        - protocol: UDP
          port: 53
EOF
echo "✅ Network policy created"

echo ""
echo "→ Creating pod security policy..."
cat > "$K8S_DIR/pod-security-policy.yaml" << 'EOF'
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: securebank-restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  readOnlyRootFilesystem: true
EOF
echo "✅ Pod security policy created"

echo ""
echo "✅ Kubernetes auto-fixes complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Review changes: cd $K8S_DIR && git diff"
echo "   2. Apply changes: kubectl apply -f ."
echo "   3. Verify pods: kubectl get pods -n securebank"
