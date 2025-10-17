#!/usr/bin/env python3
"""
MCP Tool Builder - Create tools from natural language prompts
Powered by OpenAI for intelligent tool generation
"""

import asyncio
import json
import logging
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MCPToolBuilder:
    """
    Generates MCP tools from natural language descriptions using AI
    """

    def __init__(self):
        self.tools_dir = Path("jamesos/memory/mcp_tools")
        self.tools_dir.mkdir(parents=True, exist_ok=True)

        self.scripts_dir = Path("scripts")
        self.scripts_dir.mkdir(parents=True, exist_ok=True)

        # Tool categories and templates
        self.tool_categories = {
            "system": {
                "description": "System administration and monitoring",
                "templates": ["service_restart", "system_info", "process_monitor"],
                "safety_level": "high",
            },
            "deployment": {
                "description": "Application deployment and management",
                "templates": ["deploy_app", "rollback", "health_check"],
                "safety_level": "medium",
            },
            "monitoring": {
                "description": "System and application monitoring",
                "templates": ["log_analysis", "metric_collection", "alert_check"],
                "safety_level": "low",
            },
            "database": {
                "description": "Database operations and maintenance",
                "templates": ["backup_db", "query_data", "db_health"],
                "safety_level": "high",
            },
            "networking": {
                "description": "Network configuration and troubleshooting",
                "templates": ["port_check", "connectivity_test", "firewall_rule"],
                "safety_level": "medium",
            },
        }

        # Initialize OpenAI client if available
        self.openai_client = None
        self._init_openai()

    def _init_openai(self):
        """Initialize OpenAI client for tool generation"""
        try:
            import os

            import openai

            if os.getenv("OPENAI_API_KEY"):
                self.openai_client = openai.OpenAI()
                logger.info("OpenAI client initialized for tool generation")
            else:
                logger.warning("OPENAI_API_KEY not found, using fallback generation")

        except ImportError:
            logger.warning("OpenAI not available, using template-based generation")

    async def create_tool_from_prompt(
        self, prompt: str, category: str = None, safety_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        Create an MCP tool from a natural language prompt

        Args:
            prompt: Natural language description of the tool
            category: Tool category (system, deployment, etc.)
            safety_level: Safety level (low, medium, high)

        Returns:
            Dictionary containing tool creation results
        """
        try:
            logger.info(f"Creating tool from prompt: '{prompt[:100]}...'")

            # Analyze the prompt to extract requirements
            analysis = self._analyze_prompt(prompt)

            # Determine category if not provided
            if not category:
                category = self._determine_category(prompt, analysis)

            # Generate tool definition
            if self.openai_client:
                tool_definition = await self._generate_with_openai(
                    prompt, analysis, category, safety_level
                )
            else:
                tool_definition = await self._generate_with_templates(
                    prompt, analysis, category, safety_level
                )

            # Validate the generated tool
            validation_result = self._validate_tool(tool_definition)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "Tool validation failed",
                    "details": validation_result["errors"],
                    "tool_definition": tool_definition,
                }

            # Save the tool
            tool_file = self._save_tool(tool_definition)

            # Generate accompanying script if needed
            script_file = None
            if tool_definition.get("needs_script", False):
                script_file = await self._generate_script(tool_definition)

            return {
                "success": True,
                "tool_name": tool_definition["tool_name"],
                "tool_file": str(tool_file),
                "script_file": str(script_file) if script_file else None,
                "category": category,
                "safety_level": safety_level,
                "auto_execute": tool_definition.get("auto_execute", False),
                "requires_confirmation": tool_definition.get(
                    "requires_confirmation", True
                ),
                "tool_definition": tool_definition,
            }

        except Exception as e:
            logger.error(f"Tool creation failed: {e}")
            return {"success": False, "error": str(e), "prompt": prompt}

    def _analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt to extract requirements and intent"""

        analysis = {
            "intent": "unknown",
            "action_words": [],
            "target_resources": [],
            "parameters": [],
            "safety_indicators": [],
            "complexity": "medium",
        }

        prompt_lower = prompt.lower()

        # Detect intent from action words
        action_patterns = {
            "restart": ["restart", "reboot", "reload"],
            "monitor": ["monitor", "check", "watch", "status"],
            "deploy": ["deploy", "install", "setup", "configure"],
            "backup": ["backup", "save", "archive", "export"],
            "query": ["query", "search", "find", "list", "show"],
            "create": ["create", "make", "generate", "build"],
            "delete": ["delete", "remove", "destroy", "clean"],
            "update": ["update", "modify", "change", "edit"],
        }

        for intent, words in action_patterns.items():
            if any(word in prompt_lower for word in words):
                analysis["intent"] = intent
                analysis["action_words"].extend([w for w in words if w in prompt_lower])
                break

        # Detect target resources
        resource_patterns = [
            r"\b(nginx|apache|docker|kubernetes|mysql|postgres|redis)\b",
            r"\b(service|server|database|container|pod|deployment)\b",
            r"\b(file|directory|log|config|certificate)\b",
        ]

        for pattern in resource_patterns:
            matches = re.findall(pattern, prompt_lower)
            analysis["target_resources"].extend(matches)

        # Detect parameters
        param_patterns = [
            r"--(\w+)",  # Command line flags
            r"-(\w)",  # Short flags
            r"\$\{(\w+)\}",  # Variable placeholders
            r"\{(\w+)\}",  # Template variables
        ]

        for pattern in param_patterns:
            matches = re.findall(pattern, prompt)
            analysis["parameters"].extend(matches)

        # Detect safety indicators
        safety_patterns = {
            "dangerous": ["delete", "remove", "destroy", "format", "rm -rf", "DROP"],
            "moderate": ["restart", "stop", "kill", "modify", "change"],
            "safe": ["status", "list", "show", "read", "get", "info"],
        }

        for level, patterns in safety_patterns.items():
            if any(pattern in prompt_lower for pattern in patterns):
                analysis["safety_indicators"].append(level)

        # Determine complexity
        if len(analysis["parameters"]) > 3 or "script" in prompt_lower:
            analysis["complexity"] = "high"
        elif len(analysis["action_words"]) > 1:
            analysis["complexity"] = "medium"
        else:
            analysis["complexity"] = "low"

        return analysis

    def _determine_category(self, prompt: str, analysis: Dict[str, Any]) -> str:
        """Determine tool category based on prompt and analysis"""

        prompt_lower = prompt.lower()

        # Category keywords
        category_keywords = {
            "system": ["system", "service", "process", "cpu", "memory", "disk"],
            "deployment": ["deploy", "build", "release", "rollback", "version"],
            "monitoring": ["monitor", "alert", "log", "metric", "health", "status"],
            "database": ["database", "db", "sql", "mysql", "postgres", "backup"],
            "networking": ["network", "port", "firewall", "connectivity", "ping"],
        }

        # Score each category
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            if analysis["target_resources"]:
                # Boost score if target resources match category
                resource_matches = sum(
                    1
                    for resource in analysis["target_resources"]
                    if resource in keywords
                )
                score += resource_matches * 2
            category_scores[category] = score

        # Return category with highest score, default to 'system'
        if category_scores:
            return max(category_scores, key=category_scores.get)

        return "system"

    async def _generate_with_openai(
        self, prompt: str, analysis: Dict[str, Any], category: str, safety_level: str
    ) -> Dict[str, Any]:
        """Generate tool using OpenAI with enhanced Giancarlo-style prompting"""

        system_prompt = f"""You are James, Giancarlo Esposito's AI assistant character. You create precise, professional MCP tools with his signature attention to detail and strategic thinking.

TASK: Create a JSON tool definition for: "{prompt}"

CONTEXT:
- Category: {category}
- Safety Level: {safety_level}
- Analysis: {json.dumps(analysis, indent=2)}

REQUIREMENTS - Generate a complete MCP tool with these exact fields:
{{
  "tool_name": "snake_case_name",
  "description": "Clear, professional description of functionality",
  "command": "Safe, tested shell command with error handling",
  "task_type": "{category}",
  "auto_execute": boolean (false for operations requiring confirmation),
  "requires_confirmation": boolean (true for system-changing operations),
  "tags": ["relevant", "descriptive", "tags"],
  "examples": [
    "Natural language examples that would trigger this tool",
    "How users would ask James to run this",
    "Alternative phrasings for the same request"
  ],
  "created_at": "ISO timestamp",
  "parameters": {{
    "param_name": {{
      "type": "string|integer|boolean",
      "description": "What this parameter controls",
      "required": boolean,
      "default": "default_value_if_any"
    }}
  }},
  "safety_notes": "Professional explanation of safety considerations",
  "usage_context": "When and why this tool should be used"
}}

SAFETY PROTOCOL:
- Commands with rm, dd, format, shutdown: auto_execute=false, requires_confirmation=true
- System modifications: requires_confirmation=true
- Read-only operations: auto_execute=true (if safe)
- Include proper error handling in commands
- Use full paths and validation

COMMAND CONSTRUCTION:
- Use defensive programming practices
- Include error checking and user feedback
- Prefer safer alternatives when possible
- Add timeout protection for long operations
- Include success/failure indicators

Return ONLY the JSON object, no markdown or explanation."""

        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Create a professional tool for: {prompt}",
                    },
                ],
                temperature=0.1,
                max_tokens=1500,
            )

            content = response.choices[0].message.content.strip()

            # Clean up the response - remove markdown if present
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()

            # Extract JSON from response
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                tool_definition = json.loads(json_match.group())

                # Ensure required fields with professional defaults
                tool_definition.setdefault("created_at", datetime.utcnow().isoformat())
                tool_definition.setdefault("updated_at", datetime.utcnow().isoformat())
                tool_definition.setdefault("generated_by", "James AI Assistant")
                tool_definition.setdefault("version", "1.0")

                return tool_definition
            else:
                raise ValueError("No valid JSON found in OpenAI response")

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            # Fallback to template generation
            return await self._generate_with_templates(
                prompt, analysis, category, safety_level
            )

    async def _generate_with_templates(
        self, prompt: str, analysis: Dict[str, Any], category: str, safety_level: str
    ) -> Dict[str, Any]:
        """Generate tool using templates as fallback"""

        # Generate basic tool name
        tool_name = self._generate_tool_name(prompt, analysis)

        # Generate command based on intent
        command = self._generate_command(prompt, analysis)

        # Determine safety settings
        auto_execute = (
            safety_level == "low" and "dangerous" not in analysis["safety_indicators"]
        )
        requires_confirmation = (
            "dangerous" in analysis["safety_indicators"] or safety_level == "high"
        )

        # Generate tags
        tags = [category, analysis["intent"]]
        tags.extend(analysis["target_resources"][:3])  # Add up to 3 resources

        # Generate examples
        examples = self._generate_examples(prompt, tool_name)

        tool_definition = {
            "tool_name": tool_name,
            "description": f"Generated tool: {prompt}",
            "command": command,
            "task_type": category,
            "auto_execute": auto_execute,
            "requires_confirmation": requires_confirmation,
            "tags": tags,
            "examples": examples,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "generated_from_prompt": prompt,
        }

        return tool_definition

    def _generate_tool_name(self, prompt: str, analysis: Dict[str, Any]) -> str:
        """Generate a tool name from prompt and analysis"""

        # Start with intent
        name_parts = (
            [analysis["intent"]] if analysis["intent"] != "unknown" else ["custom"]
        )

        # Add main resource if identified
        if analysis["target_resources"]:
            name_parts.append(analysis["target_resources"][0])

        # Add distinguishing word from prompt
        prompt_words = re.findall(r"\b\w{3,}\b", prompt.lower())
        interesting_words = [
            w
            for w in prompt_words
            if w not in ["the", "and", "for", "with", "that", "this"]
        ]

        if interesting_words and len(name_parts) < 3:
            name_parts.append(interesting_words[0])

        # Join and clean
        tool_name = "_".join(name_parts)
        tool_name = re.sub(r"[^\w_]", "", tool_name)

        # Ensure uniqueness
        counter = 1
        base_name = tool_name
        while (self.tools_dir / f"{tool_name}.json").exists():
            tool_name = f"{base_name}_{counter}"
            counter += 1

        return tool_name

    def _generate_command(self, prompt: str, analysis: Dict[str, Any]) -> str:
        """Generate a command based on the prompt and analysis"""

        intent = analysis["intent"]
        resources = analysis["target_resources"]

        # Command templates by intent
        if intent == "restart" and "service" in prompt.lower():
            service_name = next(
                (r for r in resources if r in ["nginx", "apache", "docker"]), "nginx"
            )
            return f"sudo systemctl restart {service_name}"

        elif intent == "monitor" or intent == "check":
            if "status" in prompt.lower():
                return "systemctl status --no-pager"
            elif "disk" in prompt.lower():
                return "df -h"
            elif "memory" in prompt.lower():
                return "free -h"
            else:
                return "uptime && free -h && df -h"

        elif intent == "query" or "list" in prompt.lower():
            if "process" in prompt.lower():
                return "ps aux --sort=-%cpu | head -20"
            elif "service" in prompt.lower():
                return "systemctl list-units --type=service --state=running"
            else:
                return "ls -la"

        elif intent == "backup":
            return "tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz /path/to/data"

        elif intent == "deploy":
            return "echo 'Deployment command - please customize for your environment'"

        else:
            # Generic command based on prompt keywords
            if "docker" in prompt.lower():
                return "docker ps"
            elif "kubernetes" in prompt.lower() or "k8s" in prompt.lower():
                return "kubectl get pods"
            else:
                return f"echo 'Custom command for: {prompt}'"

    def _generate_examples(self, prompt: str, tool_name: str) -> List[str]:
        """Generate example queries for the tool"""

        examples = [prompt]  # Original prompt is always an example

        # Generate variations
        tool_display_name = tool_name.replace("_", " ")
        examples.extend(
            [
                f"Run {tool_display_name}",
                f"Execute {tool_display_name}",
                f"Can you {tool_display_name}?",
            ]
        )

        return examples[:4]  # Limit to 4 examples

    def _validate_tool(self, tool_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a tool definition"""

        errors = []
        required_fields = ["tool_name", "description", "command", "task_type"]

        # Check required fields
        for field in required_fields:
            if field not in tool_definition:
                errors.append(f"Missing required field: {field}")

        # Validate tool name
        if "tool_name" in tool_definition:
            name = tool_definition["tool_name"]
            if not re.match(r"^[a-z][a-z0-9_]*$", name):
                errors.append("Tool name must be snake_case and start with a letter")

        # Check for dangerous commands
        if "command" in tool_definition:
            command = tool_definition["command"].lower()
            dangerous_patterns = [
                "rm -rf",
                "dd if=",
                "format",
                "> /dev/",
                "shutdown",
                "reboot",
            ]

            for pattern in dangerous_patterns:
                if pattern in command:
                    if tool_definition.get("auto_execute", False):
                        errors.append(
                            f"Dangerous command '{pattern}' cannot have auto_execute=true"
                        )
                    if not tool_definition.get("requires_confirmation", True):
                        errors.append(
                            f"Dangerous command '{pattern}' must require confirmation"
                        )

        return {"valid": len(errors) == 0, "errors": errors}

    def _save_tool(self, tool_definition: Dict[str, Any]) -> Path:
        """Save tool definition to file"""

        tool_name = tool_definition["tool_name"]
        tool_file = self.tools_dir / f"{tool_name}.json"

        # Ensure pretty formatting
        with open(tool_file, "w") as f:
            json.dump(tool_definition, f, indent=2, sort_keys=True)

        logger.info(f"Saved tool: {tool_file}")
        return tool_file

    async def _generate_script(self, tool_definition: Dict[str, Any]) -> Optional[Path]:
        """Generate a script file for complex tools"""

        if tool_definition.get("complexity") != "high":
            return None

        tool_name = tool_definition["tool_name"]
        script_file = self.scripts_dir / f"{tool_name}.py"

        # Generate basic Python script template
        script_content = f'''#!/usr/bin/env python3
"""
Generated script for {tool_name}
Description: {tool_definition.get("description", "Custom tool")}
"""

import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main execution function"""
    try:
        logger.info("Executing {tool_name}")
        
        # TODO: Implement the actual functionality
        command = "{tool_definition.get("command", "echo 'Not implemented'")}"
        
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return 0
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {{e}}")
        print(f"Error: {{e}}")
        return 1
        
    except Exception as e:
        logger.error(f"Unexpected error: {{e}}")
        print(f"Error: {{e}}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''

        with open(script_file, "w") as f:
            f.write(script_content)

        # Make executable
        script_file.chmod(0o755)

        logger.info(f"Generated script: {script_file}")
        return script_file

    def list_generated_tools(self) -> List[Dict[str, Any]]:
        """List all generated tools"""

        tools = []

        for tool_file in self.tools_dir.glob("*.json"):
            try:
                with open(tool_file) as f:
                    tool_data = json.load(f)

                # Add file metadata
                tool_data["file_path"] = str(tool_file)
                tool_data["file_size"] = tool_file.stat().st_size
                tool_data["generated"] = "generated_from_prompt" in tool_data

                tools.append(tool_data)

            except Exception as e:
                logger.warning(f"Error loading tool {tool_file}: {e}")

        return sorted(tools, key=lambda x: x.get("created_at", ""), reverse=True)


async def main():
    """CLI interface for tool builder"""
    import argparse

    parser = argparse.ArgumentParser(description="Build MCP tools from prompts")
    parser.add_argument("--prompt", "-p", required=True, help="Tool description prompt")
    parser.add_argument(
        "--category",
        "-c",
        choices=["system", "deployment", "monitoring", "database", "networking"],
        help="Tool category",
    )
    parser.add_argument(
        "--safety",
        "-s",
        choices=["low", "medium", "high"],
        default="medium",
        help="Safety level",
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="List generated tools"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    builder = MCPToolBuilder()

    if args.list:
        tools = builder.list_generated_tools()
        print(f"📋 Found {len(tools)} generated tools:")
        for i, tool in enumerate(tools, 1):
            generated = " (generated)" if tool.get("generated") else ""
            print(
                f"   {i}. {tool['tool_name']}: {tool.get('description', 'No description')}{generated}"
            )
        return

    print(f"🛠️  Creating tool from prompt: '{args.prompt}'")

    result = await builder.create_tool_from_prompt(
        prompt=args.prompt, category=args.category, safety_level=args.safety
    )

    if result["success"]:
        print(f"✅ Tool created successfully:")
        print(f"   Name: {result['tool_name']}")
        print(f"   File: {result['tool_file']}")
        print(f"   Category: {result['category']}")
        print(f"   Auto-execute: {result['auto_execute']}")
        print(f"   Requires confirmation: {result['requires_confirmation']}")

        if result.get("script_file"):
            print(f"   Script: {result['script_file']}")

    else:
        print(f"❌ Tool creation failed:")
        print(f"   Error: {result['error']}")
        if result.get("details"):
            for detail in result["details"]:
                print(f"   - {detail}")


# Global tool builder instance
tool_builder = MCPToolBuilder()


async def create_mcp_tool(name: str, description: str, **kwargs) -> Dict[str, Any]:
    """
    Create an MCP tool from name and description

    Args:
        name: Tool name
        description: Tool description
        **kwargs: Additional parameters

    Returns:
        Tool creation result
    """
    try:
        result = await tool_builder.create_tool_from_prompt(
            prompt=f"{name}: {description}",
            category=kwargs.get("category"),
            safety_level=kwargs.get("safety_level", "medium"),
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    asyncio.run(main())
