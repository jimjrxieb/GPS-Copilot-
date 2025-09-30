#!/usr/bin/env python3
"""
OPA Policy Generator for GP-Copilot/Jade
Converts scan findings into preventive Gatekeeper policies

This is what makes Jade intelligent - it learns from violations
and generates policies to prevent them.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class OpaPolicyGenerator:
    """Generates Gatekeeper ConstraintTemplates from security scan results"""

    def __init__(self):
        self.output_dir = Path("/home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/policies/generated")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_from_violations(self, scan_results: dict) -> List[str]:
        """Convert scan findings into preventive OPA policies"""
        policies = []

        # Analyze findings and generate appropriate policies
        for finding in scan_results.get('findings', []):
            msg = finding.get('msg', '').lower()

            if 'privileged' in msg:
                policies.append(self._generate_privileged_policy())
            elif 'root' in msg or 'uid 0' in msg:
                policies.append(self._generate_nonroot_policy())
            elif 'resource' in msg and 'limit' in msg:
                policies.append(self._generate_resource_limits_policy())
            elif 'host' in msg and 'network' in msg:
                policies.append(self._generate_host_network_policy())
            elif 'label' in msg:
                policies.append(self._generate_required_labels_policy())

        return policies

    def _generate_privileged_policy(self) -> str:
        """Generate policy to prevent privileged containers"""
        policy = {
            'apiVersion': 'templates.gatekeeper.sh/v1beta1',
            'kind': 'ConstraintTemplate',
            'metadata': {
                'name': 'k8sdenyprivileged',
                'annotations': {
                    'generated-by': 'jade-policy-generator',
                    'compliance': 'CIS-5.2.5',
                    'description': 'Prevent privileged containers'
                }
            },
            'spec': {
                'crd': {
                    'spec': {
                        'names': {
                            'kind': 'K8sDenyPrivileged'
                        },
                        'validation': {
                            'openAPIV3Schema': {
                                'type': 'object'
                            }
                        }
                    }
                },
                'targets': [{
                    'target': 'admission.k8s.gatekeeper.sh',
                    'rego': '''package k8sdenyprivileged

violation[{"msg": msg}] {
    container := input.review.object.spec.containers[_]
    container.securityContext.privileged == true
    msg := sprintf("Container %v cannot run in privileged mode", [container.name])
}'''
                }]
            }
        }

        # Save policy
        policy_file = self.output_dir / "deny-privileged.yaml"
        with open(policy_file, 'w') as f:
            yaml.dump(policy, f)

        return str(policy_file)

    def _generate_nonroot_policy(self) -> str:
        """Generate policy to require non-root users"""
        policy = {
            'apiVersion': 'templates.gatekeeper.sh/v1beta1',
            'kind': 'ConstraintTemplate',
            'metadata': {
                'name': 'k8srequirenonroot',
                'annotations': {
                    'generated-by': 'jade-policy-generator',
                    'compliance': 'CIS-5.2.6',
                    'description': 'Require containers to run as non-root'
                }
            },
            'spec': {
                'crd': {
                    'spec': {
                        'names': {
                            'kind': 'K8sRequireNonRoot'
                        },
                        'validation': {
                            'openAPIV3Schema': {
                                'type': 'object'
                            }
                        }
                    }
                },
                'targets': [{
                    'target': 'admission.k8s.gatekeeper.sh',
                    'rego': '''package k8srequirenonroot

violation[{"msg": msg}] {
    container := input.review.object.spec.containers[_]
    has_field(container.securityContext, "runAsUser")
    container.securityContext.runAsUser == 0
    msg := sprintf("Container %v cannot run as root (UID 0)", [container.name])
}

violation[{"msg": msg}] {
    container := input.review.object.spec.containers[_]
    not container.securityContext.runAsNonRoot
    not container.securityContext.runAsUser
    msg := sprintf("Container %v must set runAsNonRoot or runAsUser", [container.name])
}

has_field(object, field) {
    object[field]
}'''
                }]
            }
        }

        policy_file = self.output_dir / "require-nonroot.yaml"
        with open(policy_file, 'w') as f:
            yaml.dump(policy, f)

        return str(policy_file)

    def _generate_resource_limits_policy(self) -> str:
        """Generate policy to require resource limits"""
        policy = {
            'apiVersion': 'templates.gatekeeper.sh/v1beta1',
            'kind': 'ConstraintTemplate',
            'metadata': {
                'name': 'k8srequireresourcelimits',
                'annotations': {
                    'generated-by': 'jade-policy-generator',
                    'description': 'Require resource limits on containers'
                }
            },
            'spec': {
                'crd': {
                    'spec': {
                        'names': {
                            'kind': 'K8sRequireResourceLimits'
                        },
                        'validation': {
                            'openAPIV3Schema': {
                                'type': 'object',
                                'properties': {
                                    'cpu': {'type': 'string'},
                                    'memory': {'type': 'string'}
                                }
                            }
                        }
                    }
                },
                'targets': [{
                    'target': 'admission.k8s.gatekeeper.sh',
                    'rego': '''package k8srequireresourcelimits

violation[{"msg": msg}] {
    container := input.review.object.spec.containers[_]
    not container.resources.limits.memory
    msg := sprintf("Container %v must specify memory limits", [container.name])
}

violation[{"msg": msg}] {
    container := input.review.object.spec.containers[_]
    not container.resources.limits.cpu
    msg := sprintf("Container %v must specify CPU limits", [container.name])
}'''
                }]
            }
        }

        policy_file = self.output_dir / "require-resource-limits.yaml"
        with open(policy_file, 'w') as f:
            yaml.dump(policy, f)

        return str(policy_file)

    def _generate_host_network_policy(self) -> str:
        """Generate policy to prevent host network usage"""
        policy = {
            'apiVersion': 'templates.gatekeeper.sh/v1beta1',
            'kind': 'ConstraintTemplate',
            'metadata': {
                'name': 'k8sdenyhostnetwork',
                'annotations': {
                    'generated-by': 'jade-policy-generator',
                    'compliance': 'CIS-5.2.4',
                    'description': 'Prevent use of host network'
                }
            },
            'spec': {
                'crd': {
                    'spec': {
                        'names': {
                            'kind': 'K8sDenyHostNetwork'
                        },
                        'validation': {
                            'openAPIV3Schema': {
                                'type': 'object'
                            }
                        }
                    }
                },
                'targets': [{
                    'target': 'admission.k8s.gatekeeper.sh',
                    'rego': '''package k8sdenyhostnetwork

violation[{"msg": msg}] {
    input.review.object.spec.hostNetwork == true
    msg := "Pod cannot use hostNetwork"
}

violation[{"msg": msg}] {
    input.review.object.spec.hostPID == true
    msg := "Pod cannot use hostPID"
}

violation[{"msg": msg}] {
    input.review.object.spec.hostIPC == true
    msg := "Pod cannot use hostIPC"
}'''
                }]
            }
        }

        policy_file = self.output_dir / "deny-host-network.yaml"
        with open(policy_file, 'w') as f:
            yaml.dump(policy, f)

        return str(policy_file)

    def _generate_required_labels_policy(self) -> str:
        """Generate policy to require compliance labels"""
        policy = {
            'apiVersion': 'templates.gatekeeper.sh/v1beta1',
            'kind': 'ConstraintTemplate',
            'metadata': {
                'name': 'k8srequiredlabels',
                'annotations': {
                    'generated-by': 'jade-policy-generator',
                    'compliance': 'SOC2-CC6.1',
                    'description': 'Require compliance labels'
                }
            },
            'spec': {
                'crd': {
                    'spec': {
                        'names': {
                            'kind': 'K8sRequiredLabels'
                        },
                        'validation': {
                            'openAPIV3Schema': {
                                'type': 'object',
                                'properties': {
                                    'labels': {
                                        'type': 'array',
                                        'items': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    }
                },
                'targets': [{
                    'target': 'admission.k8s.gatekeeper.sh',
                    'rego': '''package k8srequiredlabels

violation[{"msg": msg}] {
    required := input.parameters.labels[_]
    provided := input.review.object.metadata.labels
    not provided[required]
    msg := sprintf("Resource missing required label: %v", [required])
}'''
                }]
            }
        }

        policy_file = self.output_dir / "require-labels.yaml"
        with open(policy_file, 'w') as f:
            yaml.dump(policy, f)

        return str(policy_file)

    def generate_constraint_from_template(self, template_name: str, config: dict) -> str:
        """Generate a Constraint that uses a ConstraintTemplate"""
        constraint = {
            'apiVersion': 'constraints.gatekeeper.sh/v1beta1',
            'kind': template_name,
            'metadata': {
                'name': config.get('name', f"{template_name.lower()}-constraint"),
                'annotations': {
                    'generated-by': 'jade-policy-generator'
                }
            },
            'spec': {
                'enforcementAction': config.get('enforcement', 'deny'),
                'match': {
                    'kinds': config.get('kinds', [
                        {'apiGroups': ['', 'apps'], 'kinds': ['Pod', 'Deployment']}
                    ]),
                    'namespaces': config.get('namespaces', ['default']),
                    'excludedNamespaces': config.get('excludedNamespaces', ['kube-system', 'gatekeeper-system'])
                }
            }
        }

        if config.get('parameters'):
            constraint['spec']['parameters'] = config['parameters']

        constraint_file = self.output_dir / f"{config.get('name', template_name.lower())}-constraint.yaml"
        with open(constraint_file, 'w') as f:
            yaml.dump(constraint, f)

        return str(constraint_file)


def main():
    """Test the policy generator"""
    generator = OpaPolicyGenerator()

    # Simulate scan results with violations
    scan_results = {
        'findings': [
            {'msg': 'Container running in privileged mode'},
            {'msg': 'Container running as root user (UID 0)'},
            {'msg': 'Container missing resource limits'},
            {'msg': 'Pod using host network'},
            {'msg': 'Resource missing required labels'}
        ]
    }

    # Generate policies
    policies = generator.generate_from_violations(scan_results)

    print(f"✅ Generated {len(policies)} Gatekeeper policies:")
    for policy in policies:
        print(f"   📄 {policy}")

    # Generate constraints
    constraint = generator.generate_constraint_from_template(
        'K8sDenyPrivileged',
        {
            'name': 'deny-privileged-production',
            'namespaces': ['production', 'staging'],
            'enforcement': 'deny'
        }
    )
    print(f"   📄 {constraint}")

    print("\n🎯 Policies ready for deployment to cluster!")


if __name__ == "__main__":
    main()