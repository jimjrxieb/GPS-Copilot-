"""
Base Tool Registry for Jade's Agentic System

This is the foundation of Jade's tool-based architecture, similar to how
Claude Code has access to tools like Read, Write, Edit, etc.

Jade gets access to:
- Scanner tools (Bandit, Trivy, OPA, Gitleaks, etc.)
- Fixer tools (automated remediation for known patterns)
- Validator tools (verify fixes worked)
"""

from typing import Callable, Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class ToolCategory(Enum):
    """Categories of tools available to Jade"""
    SCANNER = "scanner"
    FIXER = "fixer"
    VALIDATOR = "validator"
    ANALYZER = "analyzer"
    REPORTER = "reporter"


class ToolSeverity(Enum):
    """Severity level for tools that require approval"""
    SAFE = "safe"           # Read-only, no changes
    LOW = "low"             # Minor changes, auto-approve
    MEDIUM = "medium"       # Moderate changes, notify user
    HIGH = "high"           # Significant changes, require approval
    CRITICAL = "critical"   # Major changes, require explicit approval


@dataclass
class Tool:
    """
    A tool that Jade can use for autonomous security engineering

    Similar to Claude Code's tools (Read, Write, Edit), but specialized
    for security automation (Scan, Fix, Validate, etc.)
    """
    name: str
    description: str
    function: Callable
    category: ToolCategory
    severity: ToolSeverity = ToolSeverity.SAFE
    parameters: Dict[str, Any] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)
    requires_approval: bool = False
    output_format: str = "json"

    def __post_init__(self):
        """Set requires_approval based on severity"""
        if self.severity in [ToolSeverity.HIGH, ToolSeverity.CRITICAL]:
            self.requires_approval = True

    def to_llm_schema(self) -> Dict[str, Any]:
        """
        Convert tool to schema for LLM function calling

        This is what gets passed to Qwen/OpenAI-compatible models
        so they know what tools are available
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": self.parameters,
                "required": [k for k, v in self.parameters.items() if v.get("required", False)]
            },
            "category": self.category.value,
            "severity": self.severity.value,
            "requires_approval": self.requires_approval,
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters

        Returns standardized result format:
        {
            "success": bool,
            "data": Any,
            "error": Optional[str],
            "metadata": {
                "tool_name": str,
                "category": str,
                "timestamp": str,
            }
        }
        """
        import time

        try:
            result = self.function(**kwargs)
            return {
                "success": True,
                "data": result,
                "error": None,
                "metadata": {
                    "tool_name": self.name,
                    "category": self.category.value,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "metadata": {
                    "tool_name": self.name,
                    "category": self.category.value,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            }


class ToolRegistry:
    """
    Central registry of all tools available to Jade

    This is like Claude Code's tool palette, but for security automation.
    When Jade needs to scan, fix, or validate something, it looks here.
    """

    _tools: Dict[str, Tool] = {}
    _categories: Dict[ToolCategory, List[str]] = {cat: [] for cat in ToolCategory}

    @classmethod
    def register(cls,
                 name: str,
                 description: str,
                 category: ToolCategory,
                 severity: ToolSeverity = ToolSeverity.SAFE,
                 parameters: Optional[Dict[str, Any]] = None,
                 examples: Optional[List[str]] = None):
        """
        Decorator to register a function as a tool

        Usage:
        @ToolRegistry.register(
            name="scan_with_bandit",
            description="Scan Python code for security issues",
            category=ToolCategory.SCANNER,
            severity=ToolSeverity.SAFE,
            parameters={
                "target_path": {
                    "type": "string",
                    "description": "Path to scan",
                    "required": True
                }
            }
        )
        def scan_bandit(target_path: str) -> dict:
            # Implementation
            pass
        """
        def decorator(func: Callable):
            tool = Tool(
                name=name,
                description=description,
                function=func,
                category=category,
                severity=severity,
                parameters=parameters or {},
                examples=examples or [],
            )

            cls._tools[name] = tool
            cls._categories[category].append(name)

            return func
        return decorator

    @classmethod
    def get_tool(cls, name: str) -> Optional[Tool]:
        """Get a specific tool by name"""
        return cls._tools.get(name)

    @classmethod
    def get_tools_by_category(cls, category: ToolCategory) -> List[Tool]:
        """Get all tools in a category"""
        return [cls._tools[name] for name in cls._categories[category]]

    @classmethod
    def get_all_tools(cls) -> List[Tool]:
        """Get all registered tools"""
        return list(cls._tools.values())

    @classmethod
    def get_llm_schemas(cls, category: Optional[ToolCategory] = None) -> List[Dict[str, Any]]:
        """
        Get tool schemas for LLM function calling

        This is what gets sent to the LLM so it knows what tools
        are available and how to use them.
        """
        if category:
            tools = cls.get_tools_by_category(category)
        else:
            tools = cls.get_all_tools()

        return [tool.to_llm_schema() for tool in tools]

    @classmethod
    def list_tools(cls, category: Optional[ToolCategory] = None) -> str:
        """
        Human-readable list of available tools

        Used for debugging and showing Jade what tools are available
        """
        if category:
            tools = cls.get_tools_by_category(category)
            header = f"\n=== {category.value.upper()} TOOLS ===\n"
        else:
            tools = cls.get_all_tools()
            header = "\n=== ALL AVAILABLE TOOLS ===\n"

        output = [header]
        for tool in sorted(tools, key=lambda t: (t.category.value, t.name)):
            output.append(f"\n{tool.name} ({tool.category.value})")
            output.append(f"  {tool.description}")
            output.append(f"  Severity: {tool.severity.value}")
            if tool.requires_approval:
                output.append("  ⚠️  Requires approval")

        return "\n".join(output)

    @classmethod
    def execute_tool(cls, name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool by name with given parameters

        This is the main entry point for Jade to use tools.
        Returns standardized result format.
        """
        tool = cls.get_tool(name)
        if not tool:
            return {
                "success": False,
                "data": None,
                "error": f"Tool '{name}' not found in registry",
                "metadata": {"tool_name": name}
            }

        return tool.execute(**kwargs)

    @classmethod
    def save_registry(cls, output_path: Path):
        """Save tool registry to JSON for inspection"""
        registry_data = {
            "tools": [tool.to_llm_schema() for tool in cls.get_all_tools()],
            "categories": {cat.value: names for cat, names in cls._categories.items()},
            "total_tools": len(cls._tools),
        }

        output_path.write_text(json.dumps(registry_data, indent=2))
        print(f"✅ Tool registry saved to {output_path}")