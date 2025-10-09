#!/usr/bin/env python3
"""
James UI Integration - Connect GuidePoint to James interfaces
Provides API endpoints for the Vue.js dashboard and Electron widget
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import uvicorn

# Add GP-copilot to path
GP_COPILOT_BASE = '/home/jimmie/linkops-industries/GP-copilot'
sys.path.insert(0, f'{GP_COPILOT_BASE}/GP-PLATFORM/core')
sys.path.insert(0, f'{GP_COPILOT_BASE}/james-config')  # Add james-config for gp_data_config
sys.path.insert(0, GP_COPILOT_BASE)

from james_command_router import JamesCommandRouter
from gp_data_config import GPDataConfig

# Initialize GP-DATA config
gp_config = GPDataConfig()

app = FastAPI(title="James GuidePoint UI Integration", version="1.0.0")

# Enable CORS for Vue.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize command router
router = JamesCommandRouter()

@app.get("/health")
async def health_check():
    """Health check for service monitoring"""
    return {
        "status": "healthy",
        "service": "james-guidepoint",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/guidepoint/status")
async def get_status():
    """Get GuidePoint system status for UI"""
    try:
        result = router.route_command("status")
        return {
            "status": "success",
            "projects": result.get("projects", []),
            "total_projects": result.get("total_count", 0),
            "system_status": "operational",
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/guidepoint/projects")
async def list_projects():
    """List all available projects"""
    try:
        result = router.route_command("status")
        if result["status"] == "success":
            return {
                "projects": result["projects"],
                "total_count": result["total_count"]
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to list projects"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/guidepoint/scan/{project_name}")
async def scan_project(project_name: str):
    """Scan a specific project"""
    try:
        result = router.route_command(f"scan {project_name}")

        if result["status"] == "success":
            return {
                "status": "completed",
                "project": result["project"],
                "scan_results": result.get("scan_results", {}),
                "next_steps": result.get("next_steps", []),
                "timestamp": datetime.now().isoformat()
            }
        elif result["status"] == "error":
            raise HTTPException(status_code=400, detail={
                "message": result.get("message", "Scan failed"),
                "available_projects": result.get("available_projects", [])
            })
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/guidepoint/scan/{project_name}/history")
async def get_scan_history(project_name: str):
    """Get scan history for a project"""
    try:
        results_dir = Path(gp_config.get_scans_directory())

        history = []
        if results_dir.exists():
            for scan_file in sorted(results_dir.glob("*.json"), reverse=True):
                try:
                    with open(scan_file) as f:
                        scan_data = json.load(f)

                    # Check if this scan matches the project
                    if project_name.lower() in scan_data.get("scan_info", {}).get("target", "").lower():
                        history.append({
                            "timestamp": scan_data.get("scan_info", {}).get("timestamp"),
                            "total_issues": scan_data.get("summary", {}).get("total_issues", 0),
                            "scanners_run": scan_data.get("summary", {}).get("scanners_run", 0),
                            "duration": scan_data.get("summary", {}).get("scan_duration", "Unknown"),
                            "file": scan_file.name
                        })
                except:
                    continue

        return {
            "project": project_name,
            "scan_history": history[:10],  # Last 10 scans
            "total_scans": len(history)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/guidepoint/command")
async def execute_command(command_data: dict):
    """Execute arbitrary GuidePoint command"""
    try:
        command = command_data.get("command", "")
        if not command:
            raise HTTPException(status_code=400, detail="Command is required")

        result = router.route_command(command)
        return {
            "command": command,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/guidepoint/quick-actions")
async def get_quick_actions():
    """Get available quick actions for the desktop widget"""
    return {
        "actions": [
            {
                "id": "scan",
                "label": "🔍 Quick Scan",
                "description": "Scan most recent project",
                "command": "scan Portfolio"
            },
            {
                "id": "status",
                "label": "📊 Status",
                "description": "Show system status",
                "command": "status"
            },
            {
                "id": "projects",
                "label": "📁 Projects",
                "description": "List all projects",
                "command": "status"
            }
        ]
    }

@app.get("/api/guidepoint/metrics")
async def get_metrics():
    """Get metrics for the dashboard"""
    try:
        # Get project count
        status_result = router.route_command("status")
        project_count = status_result.get("total_count", 0) if status_result["status"] == "success" else 0

        # Count recent scans from GP-DATA
        results_dir = Path(gp_config.get_scans_directory())
        recent_scans = 0
        total_issues_found = 0

        if results_dir.exists():
            for scan_file in results_dir.glob("*.json"):
                try:
                    with open(scan_file) as f:
                        scan_data = json.load(f)

                    # Count scans from last 24 hours
                    scan_time = scan_data.get("scan_info", {}).get("timestamp", "")
                    if scan_time:
                        # Simplified check - count all scans for now
                        recent_scans += 1
                        total_issues_found += scan_data.get("summary", {}).get("total_issues", 0)
                except:
                    continue

        return {
            "projects_monitored": project_count,
            "recent_scans": recent_scans,
            "total_issues_found": total_issues_found,
            "average_issues_per_scan": round(total_issues_found / max(recent_scans, 1), 1),
            "system_health": "operational",
            "last_updated": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting James GuidePoint UI Integration Service...")
    print("📊 Dashboard API: http://localhost:8003")
    print("🔗 Vue.js Integration: http://localhost:1420")
    print("🖥️ Desktop Widget Integration: Available")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info"
    )