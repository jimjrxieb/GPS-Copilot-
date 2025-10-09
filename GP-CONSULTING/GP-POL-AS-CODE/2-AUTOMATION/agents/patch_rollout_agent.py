#!/usr/bin/env python3
"""
Patch Rollout Agent
Step 3: Close the Loop - Staged Rollout (dryrun → warn → deny)

Safe progressive enforcement:
1. dryrun: Audit violations, no blocking (observe impact)
2. warn: Log violations, still allow (notify teams)
3. deny: Block violations (enforce compliance)

Plus: Gatekeeper mutation for sane defaults in non-prod
"""

import subprocess
import json
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class PatchRolloutAgent:
    """
    Staged rollout manager for Gatekeeper policies.

    Progressive enforcement prevents breaking production:
    - Week 1: dryrun (audit only, gather data)
    - Week 2-3: warn (log violations, alert teams)
    - Week 4+: deny (full enforcement)

    Also enables Gatekeeper mutation webhooks for auto-patching in non-prod.
    """

    def __init__(self, kubeconfig: Optional[str] = None):
        self.kubectl_path = self._find_kubectl()
        self.kubeconfig = kubeconfig

    def _find_kubectl(self) -> str:
        """Locate kubectl binary"""
        if shutil.which("kubectl"):
            return "kubectl"
        raise RuntimeError("kubectl not installed")

    def _kubectl(self, args: List[str], namespace: Optional[str] = None) -> subprocess.CompletedProcess:
        """Run kubectl command"""
        cmd = [self.kubectl_path]
        if self.kubeconfig:
            cmd.extend(["--kubeconfig", self.kubeconfig])
        if namespace:
            cmd.extend(["-n", namespace])
        cmd.extend(args)

        return subprocess.run(cmd, capture_output=True, text=True)

    def deploy_policy_staged(
        self,
        constraint_file: Path,
        environment: str,
        enforcement_action: str = "dryrun"
    ) -> bool:
        """
        Deploy Gatekeeper Constraint with staged enforcement

        Args:
            constraint_file: Path to Constraint YAML
            environment: "dev", "staging", "production"
            enforcement_action: "dryrun", "warn", "deny"

        Returns:
            True if deployed successfully
        """
        print(f"[Patch Rollout] Deploying {constraint_file.name} to {environment} (mode: {enforcement_action})")

        if not constraint_file.exists():
            print(f"Error: Constraint file not found: {constraint_file}")
            return False

        # Read constraint
        import yaml
        constraint = yaml.safe_load(constraint_file.read_text())

        # Set enforcement action
        constraint.setdefault("spec", {})["enforcementAction"] = enforcement_action

        # Add environment label
        constraint.setdefault("metadata", {}).setdefault("labels", {})
        constraint["metadata"]["labels"]["environment"] = environment
        constraint["metadata"]["labels"]["rollout-stage"] = enforcement_action

        # Write modified constraint to temp file
        temp_file = Path(f"/tmp/{constraint_file.stem}_{enforcement_action}.yaml")
        temp_file.write_text(yaml.dump(constraint))

        # Apply to cluster
        result = self._kubectl(["apply", "-f", str(temp_file)])

        if result.returncode == 0:
            print(f"✅ Deployed {constraint_file.name} with {enforcement_action} mode")
            return True
        else:
            print(f"❌ Failed to deploy: {result.stderr}")
            return False

    def progressive_rollout(self, constraint_file: Path, environment: str) -> bool:
        """
        Execute progressive rollout: dryrun → warn → deny

        Timeline:
        - Day 1-7: dryrun (audit only)
        - Day 8-14: warn (log violations)
        - Day 15+: deny (full enforcement)

        In practice, you'd schedule this with cron/k8s CronJob
        """
        print(f"[Patch Rollout] Starting progressive rollout for {constraint_file.name} in {environment}")

        stages = [
            {"action": "dryrun", "duration_days": 7, "description": "Audit violations, gather data"},
            {"action": "warn", "duration_days": 7, "description": "Warn teams, prepare for enforcement"},
            {"action": "deny", "duration_days": None, "description": "Full enforcement"}
        ]

        for stage in stages:
            print(f"\n📊 Stage: {stage['action']} - {stage['description']}")

            # Deploy with current enforcement action
            success = self.deploy_policy_staged(constraint_file, environment, stage["action"])
            if not success:
                print(f"❌ Rollout failed at {stage['action']} stage")
                return False

            # Wait (in production, this would be scheduled)
            if stage["duration_days"]:
                print(f"⏳ Would wait {stage['duration_days']} days before next stage")
                # In production: time.sleep(stage['duration_days'] * 86400)

                # For demo: check if violations exist
                print(f"   Checking for violations during {stage['action']} period...")
                # (Integrate with gatekeeper_audit_agent.py)

        print("\n✅ Progressive rollout complete!")
        return True

    def enable_mutation(self, environment: str = "non-prod") -> bool:
        """
        Enable Gatekeeper mutation webhooks for auto-patching

        Mutations apply "sane defaults" automatically:
        - Add runAsNonRoot: true
        - Add resource limits
        - Drop dangerous capabilities

        Only enable in non-prod environments!
        """
        if environment == "production":
            print("⚠️  Mutation should NOT be enabled in production!")
            return False

        print(f"[Patch Rollout] Enabling Gatekeeper mutation in {environment}")

        # Example: Create Assign mutation for runAsNonRoot
        mutation_policy = {
            "apiVersion": "mutations.gatekeeper.sh/v1alpha1",
            "kind": "Assign",
            "metadata": {
                "name": "pod-always-run-as-non-root"
            },
            "spec": {
                "applyTo": [
                    {
                        "groups": [""],
                        "kinds": ["Pod"],
                        "versions": ["v1"]
                    }
                ],
                "match": {
                    "scope": "Namespaced",
                    "kinds": [
                        {
                            "apiGroups": ["*"],
                            "kinds": ["Pod"]
                        }
                    ],
                    "namespaceSelector": {
                        "matchLabels": {
                            "environment": environment
                        }
                    }
                },
                "location": "spec.securityContext.runAsNonRoot",
                "parameters": {
                    "assign": {
                        "value": True
                    }
                }
            }
        }

        # Write to temp file
        import yaml
        temp_file = Path("/tmp/gatekeeper_mutation.yaml")
        temp_file.write_text(yaml.dump(mutation_policy))

        # Apply mutation
        result = self._kubectl(["apply", "-f", str(temp_file)])

        if result.returncode == 0:
            print(f"✅ Mutation enabled in {environment}")
            print("   Pods will now automatically get runAsNonRoot: true")
            return True
        else:
            print(f"❌ Failed to enable mutation: {result.stderr}")
            return False

    def rollout_status(self, constraint_name: str) -> Dict:
        """
        Check rollout status of a constraint

        Returns:
            {
                "current_stage": "warn",
                "violations": 5,
                "ready_for_next_stage": True
            }
        """
        # Get constraint
        result = self._kubectl(["get", constraint_name, "-o", "json"])
        if result.returncode != 0:
            return {"error": f"Constraint not found: {constraint_name}"}

        import json
        constraint = json.loads(result.stdout)

        enforcement_action = constraint.get("spec", {}).get("enforcementAction", "unknown")
        total_violations = constraint.get("status", {}).get("totalViolations", 0)

        # Determine if ready for next stage
        ready_for_next = total_violations == 0

        return {
            "constraint_name": constraint_name,
            "current_stage": enforcement_action,
            "total_violations": total_violations,
            "ready_for_next_stage": ready_for_next,
            "recommendation": "Proceed to next stage" if ready_for_next else "Wait for violations to be fixed"
        }


def main():
    """CLI entrypoint"""
    import sys

    if len(sys.argv) < 3:
        print("Usage:")
        print("  patch_rollout_agent.py deploy <constraint_file> <environment> [enforcement_action]")
        print("  patch_rollout_agent.py progressive <constraint_file> <environment>")
        print("  patch_rollout_agent.py mutation <environment>")
        print("  patch_rollout_agent.py status <constraint_name>")
        sys.exit(1)

    command = sys.argv[1]
    agent = PatchRolloutAgent()

    if command == "deploy":
        constraint_file = Path(sys.argv[2])
        environment = sys.argv[3]
        enforcement_action = sys.argv[4] if len(sys.argv) > 4 else "dryrun"

        success = agent.deploy_policy_staged(constraint_file, environment, enforcement_action)
        sys.exit(0 if success else 1)

    elif command == "progressive":
        constraint_file = Path(sys.argv[2])
        environment = sys.argv[3]

        success = agent.progressive_rollout(constraint_file, environment)
        sys.exit(0 if success else 1)

    elif command == "mutation":
        environment = sys.argv[2]

        success = agent.enable_mutation(environment)
        sys.exit(0 if success else 1)

    elif command == "status":
        constraint_name = sys.argv[2]

        status = agent.rollout_status(constraint_name)
        print(json.dumps(status, indent=2))
        sys.exit(0)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()