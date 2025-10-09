#!/usr/bin/env python3
"""
GuidePoint Unified API System
============================

Single, clean API interface replacing multiple competing API layers.
"""

from ..automation_engine.api.agent_gateway import app as agent_api
from ..automation_engine.api.unified.automation_api import app as automation_api

__all__ = ['agent_api', 'automation_api']