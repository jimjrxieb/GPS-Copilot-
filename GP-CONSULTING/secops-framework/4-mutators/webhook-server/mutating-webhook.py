#!/usr/bin/env python3
"""
Kubernetes Mutating Admission Webhook Server
Intercepts Pod/Deployment creation and auto-injects security defaults
"""

import os
import json
import base64
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security defaults
POD_SECURITY_CONTEXT = {
    "runAsNonRoot": True,
    "runAsUser": 1000,
    "fsGroup": 2000,
    "seccompProfile": {
        "type": "RuntimeDefault"
    }
}

CONTAINER_SECURITY_CONTEXT = {
    "allowPrivilegeEscalation": False,
    "capabilities": {
        "drop": ["ALL"]
    },
    "readOnlyRootFilesystem": True,
    "runAsNonRoot": True,
    "runAsUser": 1000
}

RESOURCE_LIMITS = {
    "limits": {
        "cpu": "500m",
        "memory": "512Mi"
    },
    "requests": {
        "cpu": "250m",
        "memory": "256Mi"
    }
}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/mutate', methods=['POST'])
def mutate():
    """
    Kubernetes admission webhook endpoint
    """
    admission_review = request.get_json()

    if not admission_review or 'request' not in admission_review:
        return jsonify({"error": "Invalid AdmissionReview"}), 400

    req = admission_review['request']
    uid = req['uid']
    kind = req['kind']['kind']
    namespace = req.get('namespace', 'default')

    logger.info(f"Mutating {kind} in namespace {namespace}")

    # Get the object from request
    obj = req.get('object', {})

    # Generate patches based on kind
    patches = []

    if kind == "Pod":
        patches = generate_pod_patches(obj)
    elif kind == "Deployment":
        patches = generate_deployment_patches(obj)

    # Build admission response
    if patches:
        patch_base64 = base64.b64encode(json.dumps(patches).encode()).decode()
        response = {
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "response": {
                "uid": uid,
                "allowed": True,
                "patchType": "JSONPatch",
                "patch": patch_base64,
                "status": {
                    "message": f"Injected {len(patches)} security defaults"
                }
            }
        }
        logger.info(f"Applied {len(patches)} patches to {kind}")
    else:
        response = {
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "response": {
                "uid": uid,
                "allowed": True
            }
        }
        logger.info(f"No patches needed for {kind}")

    return jsonify(response), 200

def generate_pod_patches(pod):
    """Generate JSONPatch operations for Pod"""
    patches = []

    # 1. Inject pod-level security context
    if 'securityContext' not in pod.get('spec', {}):
        patches.append({
            "op": "add",
            "path": "/spec/securityContext",
            "value": POD_SECURITY_CONTEXT
        })

    # 2. Inject container-level security contexts
    containers = pod.get('spec', {}).get('containers', [])
    for i, container in enumerate(containers):
        if 'securityContext' not in container:
            patches.append({
                "op": "add",
                "path": f"/spec/containers/{i}/securityContext",
                "value": CONTAINER_SECURITY_CONTEXT
            })

        # Inject resource limits
        if 'resources' not in container:
            patches.append({
                "op": "add",
                "path": f"/spec/containers/{i}/resources",
                "value": RESOURCE_LIMITS
            })

    # 3. Disable dangerous settings
    if pod.get('spec', {}).get('hostNetwork'):
        patches.append({
            "op": "replace",
            "path": "/spec/hostNetwork",
            "value": False
        })

    if pod.get('spec', {}).get('hostPID'):
        patches.append({
            "op": "replace",
            "path": "/spec/hostPID",
            "value": False
        })

    return patches

def generate_deployment_patches(deployment):
    """Generate JSONPatch operations for Deployment"""
    patches = []

    pod_spec = deployment.get('spec', {}).get('template', {}).get('spec', {})

    # 1. Inject pod-level security context
    if 'securityContext' not in pod_spec:
        patches.append({
            "op": "add",
            "path": "/spec/template/spec/securityContext",
            "value": POD_SECURITY_CONTEXT
        })

    # 2. Inject container-level security contexts
    containers = pod_spec.get('containers', [])
    for i, container in enumerate(containers):
        if 'securityContext' not in container:
            patches.append({
                "op": "add",
                "path": f"/spec/template/spec/containers/{i}/securityContext",
                "value": CONTAINER_SECURITY_CONTEXT
            })

        # Inject resource limits
        if 'resources' not in container:
            patches.append({
                "op": "add",
                "path": f"/spec/template/spec/containers/{i}/resources",
                "value": RESOURCE_LIMITS
            })

        # Block :latest tag
        if container.get('image', '').endswith(':latest'):
            patches.append({
                "op": "replace",
                "path": f"/spec/template/spec/containers/{i}/image",
                "value": container['image'].replace(':latest', ':v1.0.0')
            })

    # 3. Disable dangerous settings
    if pod_spec.get('hostNetwork'):
        patches.append({
            "op": "replace",
            "path": "/spec/template/spec/hostNetwork",
            "value": False
        })

    if pod_spec.get('hostPID'):
        patches.append({
            "op": "replace",
            "path": "/spec/template/spec/hostPID",
            "value": False
        })

    return patches

if __name__ == '__main__':
    # In production, use HTTPS with TLS certificates
    cert_file = os.getenv('TLS_CERT_FILE', '/certs/tls.crt')
    key_file = os.getenv('TLS_KEY_FILE', '/certs/tls.key')

    if os.path.exists(cert_file) and os.path.exists(key_file):
        logger.info("Starting webhook server with TLS")
        app.run(host='0.0.0.0', port=8443, ssl_context=(cert_file, key_file))
    else:
        logger.warning("TLS certificates not found. Running without TLS (DEV ONLY)")
        app.run(host='0.0.0.0', port=8080)
