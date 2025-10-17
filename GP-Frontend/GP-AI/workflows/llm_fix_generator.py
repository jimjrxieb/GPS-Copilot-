#!/usr/bin/env python3
"""
LLM-Based Fix Generator for Jade Troubleshooting Workflow

Uses LLM + RAG + Knowledge Graph context to generate intelligent fixes
for Kubernetes CrashLoopBackOff issues.

Architecture:
    RAG Context → Similar past fixes
    +
    Graph Context → Pattern → Solution relationships
    +
    LLM Reasoning → Generate fix with kubectl command
    =
    Context-aware, data-driven fix proposal
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add paths
gp_copilot_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(gp_copilot_root / "GP-Frontend" / "GP-AI" / "core"))
sys.path.insert(0, str(gp_copilot_root / "GP-Frontend" / "GP-AI" / "models"))
sys.path.insert(0, str(gp_copilot_root / "GP-Backend" / "james-config"))

try:
    from model_manager import ModelManager
except ImportError:
    print("⚠️  ModelManager not available, using fallback")
    ModelManager = None


class LLMFixGenerator:
    """
    Generate Kubernetes fixes using LLM with RAG + Graph context

    Workflow:
        1. Build context from RAG (similar fixes)
        2. Build context from Graph (pattern relationships)
        3. Create prompt with all context
        4. Generate fix using LLM
        5. Parse and validate fix JSON
    """

    def __init__(self, model_manager: Optional[Any] = None):
        """
        Initialize LLM fix generator

        Args:
            model_manager: ModelManager instance (optional)
        """
        self.model_manager = model_manager

        if not self.model_manager and ModelManager:
            try:
                self.model_manager = ModelManager()
                print("✅ LLM model loaded for fix generation")
            except Exception as e:
                print(f"⚠️  Failed to load LLM: {e}")
                self.model_manager = None

    def generate_fix(
        self,
        pod: Dict[str, Any],
        diagnostics: Dict[str, Any],
        patterns: List[str],
        rag_context: List[Dict[str, Any]],
        graph_relationships: List[Dict[str, Any]],
        project: str
    ) -> Optional[Dict[str, Any]]:
        """
        Generate fix using LLM with full context

        Args:
            pod: Pod metadata (name, namespace, container, etc.)
            diagnostics: Logs, events, detected patterns
            patterns: List of detected patterns
            rag_context: Similar past fixes from RAG
            graph_relationships: Pattern → solution from Graph
            project: Project name

        Returns:
            Fix proposal dict or None if generation fails
        """
        # Build comprehensive prompt
        prompt = self._build_prompt(
            pod=pod,
            diagnostics=diagnostics,
            patterns=patterns,
            rag_context=rag_context,
            graph_relationships=graph_relationships,
            project=project
        )

        # Generate fix using LLM
        if self.model_manager:
            try:
                response = self._generate_with_llm(prompt)
                fix = self._parse_fix_response(response, pod)
                return fix
            except Exception as e:
                print(f"⚠️  LLM generation failed: {e}")
                # Fallback to rule-based
                return self._fallback_rule_based_fix(pod, diagnostics, patterns)
        else:
            # No LLM available, use rule-based
            return self._fallback_rule_based_fix(pod, diagnostics, patterns)

    def _build_prompt(
        self,
        pod: Dict[str, Any],
        diagnostics: Dict[str, Any],
        patterns: List[str],
        rag_context: List[Dict[str, Any]],
        graph_relationships: List[Dict[str, Any]],
        project: str
    ) -> str:
        """
        Build context-rich prompt for LLM

        Prompt structure:
            1. Role and task description
            2. Pod details
            3. Detected issues and patterns
            4. Recent logs (truncated)
            5. Similar past issues (RAG)
            6. Known solution patterns (Graph)
            7. Project-specific context
            8. Output format specification
        """
        # Extract logs (truncate to 500 chars)
        logs = diagnostics.get('logs', '')[:500]

        # Format RAG context (top 3 most relevant)
        rag_examples = self._format_rag_context(rag_context[:3])

        # Format Graph context (top 3 relationships)
        graph_patterns = self._format_graph_context(graph_relationships[:3])

        prompt = f"""You are Jade, a Kubernetes troubleshooting expert with years of experience fixing CrashLoopBackOff issues.

## TASK
Generate a fix for a pod that is in CrashLoopBackOff state.

## POD DETAILS
- Name: {pod['name']}
- Namespace: {pod['namespace']}
- Container: {pod['container']}
- Image: {pod['image']}
- Restart Count: {pod['restart_count']}
- Project: {project}

## DETECTED ISSUES
Patterns: {', '.join(patterns) if patterns else 'Unknown pattern'}

## RECENT LOGS (Last 500 chars)
```
{logs}
```

## SIMILAR PAST FIXES (From Knowledge Base)
{rag_examples if rag_examples else "No similar past fixes found."}

## KNOWN SOLUTION PATTERNS (From Knowledge Graph)
{graph_patterns if graph_patterns else "No known patterns in graph."}

## INSTRUCTIONS
Based on the above context, generate a fix for this CrashLoopBackOff issue.

Your fix should:
1. Identify the root cause (why is it crashing?)
2. Propose a concrete solution (what to change?)
3. Provide the exact kubectl command to apply the fix
4. Assess the risk level (LOW/MEDIUM/HIGH)
5. Provide a confidence score (0.0-1.0) based on past success
6. Include a rollback plan (kubectl command to undo)

## GUIDELINES
- Use kubectl patch for deployment/statefulset changes
- Use kubectl apply for configuration changes
- Prefer non-destructive changes (LOW risk)
- Base confidence on number of similar successful fixes
- Always provide a rollback command

## OUTPUT FORMAT
Return ONLY a valid JSON object with this exact structure:
{{
  "pod": "{pod['name']}",
  "namespace": "{pod['namespace']}",
  "container": "{pod['container']}",
  "root_cause": "Brief explanation of why it's crashing",
  "proposed_solution": "What you're changing and why",
  "kubectl_command": "Exact kubectl command to run",
  "risk_level": "LOW or MEDIUM or HIGH",
  "confidence": 0.95,
  "based_on": "Reason for confidence (e.g., '12 similar fixes, 100% success rate')",
  "rollback_plan": "kubectl command to revert the change",
  "pattern_detected": "{patterns[0] if patterns else 'unknown'}",
  "solution_id": "descriptive_solution_name"
}}

IMPORTANT: Return ONLY the JSON object, no markdown code blocks, no explanation text."""

        return prompt

    def _format_rag_context(self, rag_results: List[Dict[str, Any]]) -> str:
        """Format RAG results into readable context"""
        if not rag_results:
            return "No similar fixes found."

        formatted = []
        for idx, result in enumerate(rag_results, 1):
            content = result.get('content', result.get('text', 'No content'))
            # Truncate long content
            if len(content) > 200:
                content = content[:200] + "..."

            score = result.get('score', result.get('distance', 0))
            if 'distance' in result:
                score = 1 - score  # Convert distance to similarity

            formatted.append(f"{idx}. (Relevance: {score:.2f}) {content}")

        return "\n".join(formatted)

    def _format_graph_context(self, relationships: List[Dict[str, Any]]) -> str:
        """Format graph relationships into readable context"""
        if not relationships:
            return "No known solution patterns."

        formatted = []
        for idx, rel in enumerate(relationships, 1):
            target = rel.get('target', 'unknown_solution')
            metadata = rel.get('metadata', {})
            success_rate = metadata.get('success_rate', 0)
            times_used = metadata.get('times_used', 0)

            formatted.append(
                f"{idx}. Solution: {target} "
                f"(Success rate: {success_rate*100:.0f}%, Used {times_used} times)"
            )

        return "\n".join(formatted)

    def _generate_with_llm(self, prompt: str) -> str:
        """
        Generate response using LLM

        Args:
            prompt: Complete prompt with context

        Returns:
            LLM response string
        """
        # Use ModelManager to generate
        response = self.model_manager.generate(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.3,  # Low temperature for more deterministic fixes
            stop=["```", "---", "###"]  # Stop at common delimiters
        )

        return response

    def _parse_fix_response(
        self,
        response: str,
        pod: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Parse LLM response into fix dict

        Args:
            response: LLM response string
            pod: Original pod data (fallback)

        Returns:
            Parsed fix dict or None
        """
        try:
            # Try to parse as JSON
            # LLM might include extra text, extract JSON portion
            response = response.strip()

            # Remove markdown code blocks if present
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]

            response = response.strip()

            # Find JSON object (starts with { ends with })
            start = response.find('{')
            end = response.rfind('}')

            if start != -1 and end != -1:
                json_str = response[start:end+1]
                fix = json.loads(json_str)

                # Validate required fields
                required_fields = [
                    'pod', 'namespace', 'root_cause', 'proposed_solution',
                    'kubectl_command', 'risk_level', 'confidence'
                ]

                if all(field in fix for field in required_fields):
                    # Ensure confidence is float
                    fix['confidence'] = float(fix['confidence'])

                    # Validate risk level
                    if fix['risk_level'] not in ['LOW', 'MEDIUM', 'HIGH']:
                        fix['risk_level'] = 'MEDIUM'

                    return fix
                else:
                    missing = [f for f in required_fields if f not in fix]
                    print(f"⚠️  LLM response missing fields: {missing}")
                    return None
            else:
                print(f"⚠️  No JSON object found in LLM response")
                return None

        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse LLM response as JSON: {e}")
            print(f"Response: {response[:200]}")
            return None
        except Exception as e:
            print(f"⚠️  Error parsing LLM response: {e}")
            return None

    def _fallback_rule_based_fix(
        self,
        pod: Dict[str, Any],
        diagnostics: Dict[str, Any],
        patterns: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Fallback to rule-based fix if LLM fails

        Same logic as Phase 1 MVP
        """
        pod_name = pod['name']
        namespace = pod['namespace']
        container = pod['container']

        if 'memory_limit_exceeded' in patterns:
            deployment_name = '-'.join(pod_name.split('-')[:-2])

            return {
                'pod': pod_name,
                'namespace': namespace,
                'container': container,
                'root_cause': 'Memory limit exceeded (OOMKilled). Container requires more memory than allocated.',
                'proposed_solution': 'Increase memory limit from current to 512Mi',
                'kubectl_command': f"kubectl patch deployment {deployment_name} -n {namespace} -p '{{\"spec\":{{\"template\":{{\"spec\":{{\"containers\":[{{\"name\":\"{container}\",\"resources\":{{\"limits\":{{\"memory\":\"512Mi\"}},\"requests\":{{\"memory\":\"384Mi\"}}}}}}]}}}}}}}}'",
                'risk_level': 'LOW',
                'confidence': 0.70,
                'based_on': 'Rule-based fallback (LLM unavailable)',
                'rollback_plan': f"kubectl patch deployment {deployment_name} -n {namespace} -p '{{\"spec\":{{\"template\":{{\"spec\":{{\"containers\":[{{\"name\":\"{container}\",\"resources\":{{\"limits\":{{\"memory\":\"256Mi\"}}}}}}]}}}}}}}}'",
                'pattern_detected': 'memory_limit_exceeded',
                'solution_id': 'increase_memory_512Mi'
            }

        elif 'dependency_unavailable' in patterns:
            deployment_name = '-'.join(pod_name.split('-')[:-2])

            return {
                'pod': pod_name,
                'namespace': namespace,
                'container': container,
                'root_cause': 'Dependency service unavailable (connection refused). Service may not be ready.',
                'proposed_solution': 'Add readiness probe and increase initialDelaySeconds',
                'kubectl_command': f"kubectl patch deployment {deployment_name} -n {namespace} -p '{{\"spec\":{{\"template\":{{\"spec\":{{\"containers\":[{{\"name\":\"{container}\",\"readinessProbe\":{{\"httpGet\":{{\"path\":\"/health\",\"port\":8080}},\"initialDelaySeconds\":30,\"periodSeconds\":10}}}}]}}}}}}}}'",
                'risk_level': 'MEDIUM',
                'confidence': 0.60,
                'based_on': 'Rule-based fallback (LLM unavailable)',
                'rollback_plan': f"kubectl rollout undo deployment {deployment_name} -n {namespace}",
                'pattern_detected': 'dependency_unavailable',
                'solution_id': 'add_readiness_probe'
            }

        else:
            return {
                'pod': pod_name,
                'namespace': namespace,
                'container': container,
                'root_cause': 'Unknown crash pattern. Manual investigation required.',
                'proposed_solution': 'Review logs manually for root cause',
                'kubectl_command': f"kubectl logs {pod_name} -n {namespace} --tail=100",
                'risk_level': 'LOW',
                'confidence': 0.30,
                'based_on': 'Rule-based fallback (unknown pattern)',
                'rollback_plan': 'N/A',
                'pattern_detected': 'unknown',
                'solution_id': 'manual_investigation'
            }


# ============================================================================
# MAIN - Test LLM fix generation
# ============================================================================

if __name__ == "__main__":
    print("🧪 Testing LLM Fix Generator")
    print("="*70)

    # Test pod
    pod = {
        'name': 'api-deployment-abc123',
        'namespace': 'default',
        'container': 'api',
        'image': 'finance-api:v1.2.3',
        'restart_count': 47
    }

    # Test diagnostics
    diagnostics = {
        'logs': 'Error: OOMKilled - Container exceeded memory limit\nFatal: Cannot allocate memory',
        'events': [{'reason': 'OOMKilled', 'message': 'Container killed due to memory'}],
        'patterns': ['memory_limit_exceeded']
    }

    # Test RAG context
    rag_context = [
        {
            'content': 'Fixed OOMKilled in FINANCE project by increasing memory from 256Mi to 512Mi. Success rate: 100% (12 fixes)',
            'score': 0.92
        },
        {
            'content': 'Memory limit issues often resolved by doubling the limit',
            'score': 0.85
        }
    ]

    # Test graph context
    graph_relationships = [
        {
            'target': 'solution_increase_memory_512Mi',
            'metadata': {'success_rate': 0.95, 'times_used': 47}
        }
    ]

    # Create generator
    generator = LLMFixGenerator()

    print("\n🔧 Generating fix with LLM...")
    fix = generator.generate_fix(
        pod=pod,
        diagnostics=diagnostics,
        patterns=['memory_limit_exceeded'],
        rag_context=rag_context,
        graph_relationships=graph_relationships,
        project='FINANCE'
    )

    if fix:
        print("\n✅ Fix generated:")
        print(f"   Root Cause: {fix['root_cause']}")
        print(f"   Solution: {fix['proposed_solution']}")
        print(f"   Risk: {fix['risk_level']}")
        print(f"   Confidence: {fix['confidence']*100:.0f}%")
        print(f"   Based On: {fix['based_on']}")
        print(f"   Command: {fix['kubectl_command'][:80]}...")
    else:
        print("\n❌ Fix generation failed")
