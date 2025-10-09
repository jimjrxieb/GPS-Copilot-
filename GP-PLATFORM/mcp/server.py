#!/usr/bin/env python3
"""
GuidePoint MCP Server
Domain-specific Model Context Protocol server for DevSecOps consulting
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from mcp import Server, types
from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions

# Import GuidePoint-specific agents
from .agents.consulting_remediation_agent import ConsultingRemediationAgent
from .agents.client_intelligence_agent import ClientIntelligenceAgent
from .agents.implementation_planning_agent import ImplementationPlanningAgent

# Import shared core components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
from mcp_client import JamesMCPClient

class GuidePointMCPServer:
    """MCP server specifically for GuidePoint consulting domain"""

    def __init__(self):
        self.server = Server("guidepoint-consulting")
        self.logger = logging.getLogger("guidepoint.mcp")

        # Initialize domain-specific agents
        self.remediation_agent = ConsultingRemediationAgent()
        self.intelligence_agent = ClientIntelligenceAgent()
        self.planning_agent = ImplementationPlanningAgent()

        # Register GuidePoint-specific tools
        self._register_consulting_tools()

    def _register_consulting_tools(self):
        """Register consulting-specific MCP tools"""

        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available GuidePoint consulting tools"""
            return [
                types.Tool(
                    name="analyze_client_security_posture",
                    description="Analyze client security posture with business context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "client_profile_id": {"type": "string"},
                            "scan_results": {"type": "object"},
                            "business_priorities": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["client_profile_id", "scan_results"]
                    }
                ),
                types.Tool(
                    name="generate_remediation_plan",
                    description="Generate client-specific remediation plan with business impact analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "client_profile_id": {"type": "string"},
                            "vulnerabilities": {"type": "array"},
                            "remediation_priority": {"type": "string", "enum": ["business_critical", "compliance_driven", "risk_balanced"]}
                        },
                        "required": ["client_profile_id", "vulnerabilities"]
                    }
                ),
                types.Tool(
                    name="create_implementation_plan",
                    description="Create step-by-step implementation plan for Kubernetes/infrastructure hardening",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "client_profile_id": {"type": "string"},
                            "target_environment": {"type": "string", "enum": ["development", "staging", "production", "critical"]},
                            "security_level": {"type": "string", "enum": ["basic", "standard", "hardened", "zero_trust"]},
                            "technology_stack": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["client_profile_id", "target_environment", "security_level"]
                    }
                ),
                types.Tool(
                    name="process_meeting_intelligence",
                    description="Process meeting notes and extract actionable consulting insights",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "client_name": {"type": "string"},
                            "meeting_notes": {"type": "string"},
                            "meeting_type": {"type": "string"},
                            "participants": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["client_name", "meeting_notes", "meeting_type"]
                    }
                ),
                types.Tool(
                    name="generate_executive_report",
                    description="Generate executive-ready security report with business intelligence",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "client_profile_id": {"type": "string"},
                            "scan_session_id": {"type": "string"},
                            "report_type": {"type": "string", "enum": ["ciso_brief", "board_summary", "compliance_audit", "business_case"]}
                        },
                        "required": ["client_profile_id", "scan_session_id", "report_type"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[types.TextContent]:
            """Handle GuidePoint consulting tool calls"""

            try:
                if name == "analyze_client_security_posture":
                    result = await self.intelligence_agent.analyze_security_posture(
                        client_profile_id=arguments["client_profile_id"],
                        scan_results=arguments["scan_results"],
                        business_priorities=arguments.get("business_priorities", [])
                    )

                elif name == "generate_remediation_plan":
                    result = await self.remediation_agent.generate_remediation_plan(
                        client_profile_id=arguments["client_profile_id"],
                        vulnerabilities=arguments["vulnerabilities"],
                        priority_strategy=arguments.get("remediation_priority", "risk_balanced")
                    )

                elif name == "create_implementation_plan":
                    result = await self.planning_agent.create_implementation_plan(
                        client_profile_id=arguments["client_profile_id"],
                        target_environment=arguments["target_environment"],
                        security_level=arguments["security_level"],
                        technology_stack=arguments.get("technology_stack", [])
                    )

                elif name == "process_meeting_intelligence":
                    result = await self.intelligence_agent.process_meeting_intelligence(
                        client_name=arguments["client_name"],
                        meeting_notes=arguments["meeting_notes"],
                        meeting_type=arguments["meeting_type"],
                        participants=arguments.get("participants", [])
                    )

                elif name == "generate_executive_report":
                    result = await self.intelligence_agent.generate_executive_report(
                        client_profile_id=arguments["client_profile_id"],
                        scan_session_id=arguments["scan_session_id"],
                        report_type=arguments["report_type"]
                    )

                else:
                    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, default=str)
                )]

            except Exception as e:
                self.logger.error(f"Tool execution error: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]

    async def start_server(self, host: str = "localhost", port: int = 8100):
        """Start the GuidePoint MCP server"""
        self.logger.info(f"Starting GuidePoint MCP server on {host}:{port}")

        # Initialize server with GuidePoint-specific configuration
        init_options = InitializationOptions(
            server_name="guidepoint-consulting",
            server_version="1.0.0",
            capabilities={
                "tools": {
                    "listChanged": True
                },
                "resources": {
                    "subscribe": True,
                    "listChanged": True
                }
            }
        )

        await self.server.run(
            host=host,
            port=port,
            init_options=init_options
        )

    async def connect_to_james_core(self, james_core_url: str = "http://localhost:8001"):
        """Connect to James Core for coordinated intelligence"""
        try:
            self.james_client = JamesMCPClient(james_core_url)
            await self.james_client.connect()
            self.logger.info("Connected to James Core intelligence")
        except Exception as e:
            self.logger.error(f"Failed to connect to James Core: {e}")

# Server startup
async def main():
    """Start GuidePoint MCP server"""
    logging.basicConfig(level=logging.INFO)

    server = GuidePointMCPServer()

    # Connect to James Core for coordinated intelligence
    await server.connect_to_james_core()

    # Start the domain-specific MCP server
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())