#!/usr/bin/env python3
"""
🎯 GuidePoint Security Platform - WORKING VERSION
Fixed imports, ready to scan your Terraform_CICD_Setup project
"""

import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Dict, Any

# Add guidepoint to path
sys.path.insert(0, '/home/jimmie/linkops-industries/James-OS/guidepoint')

# Import working scanner
from simple_guidepoint import JamesWorkingScanner

# Create scanner instance
scanner = JamesWorkingScanner()

class ScanRequest(BaseModel):
    directory: str
    project_name: str = "unknown"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print("🚀 GuidePoint Security Platform starting...")
    print("✅ James scanner: Ready")
    print("✅ Intelligence: Active")
    print("✅ Ready to scan Terraform_CICD_Setup")
    yield
    print("🛑 GuidePoint shutting down...")

# Create FastAPI app
app = FastAPI(
    title="GuidePoint Security Platform - Working",
    description="James-powered security scanner",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/scan")
async def scan_project(request: ScanRequest):
    """Scan project with James intelligence"""
    print(f"🔍 James scanning: {request.directory}")

    if not os.path.exists(request.directory):
        raise HTTPException(status_code=404, detail=f"Directory not found: {request.directory}")

    try:
        results = scanner.scan_directory(request.directory, request.project_name)
        print(f"✅ Scan complete: {results['james_analysis']['total_findings']} issues found")
        return results
    except Exception as e:
        print(f"❌ Scan failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

@app.post("/fix")
async def apply_fixes(request: ScanRequest):
    """Apply James security fixes"""
    print(f"🔧 James applying fixes to: {request.directory}")

    if not os.path.exists(request.directory):
        raise HTTPException(status_code=404, detail=f"Directory not found: {request.directory}")

    try:
        # Scan first
        scan_results = scanner.scan_directory(request.directory, request.project_name)
        original_count = len(scan_results["findings"])

        # Apply fixes
        fixes_applied = scanner.apply_fixes(request.directory, scan_results)

        # Rescan
        rescan_results = scanner.scan_directory(request.directory, request.project_name)
        remaining_count = len(rescan_results["findings"])

        improvement = ((original_count - remaining_count) / original_count * 100) if original_count > 0 else 0

        print(f"✅ Fixes complete: {len(fixes_applied)} applied, {improvement:.1f}% improvement")

        return {
            "status": "complete",
            "original_issues": original_count,
            "fixes_applied": fixes_applied,
            "remaining_issues": remaining_count,
            "improvement": f"{improvement:.1f}%",
            "james_analysis": rescan_results["james_analysis"]
        }
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        raise HTTPException(status_code=500, detail=f"Fix failed: {str(e)}")

@app.get("/scan/terraform")
async def scan_terraform_project():
    """Quick scan of Terraform_CICD_Setup project"""
    terraform_dir = "./GP-Projects/Terraform_CICD_Setup"

    if not os.path.exists(terraform_dir):
        # Try alternative locations
        alt_locations = [
            "/home/jimmie/linkops-industries/GP-Projects/Terraform_CICD_Setup",
            "/home/jimmie/linkops-industries/James-OS/guidepoint/GP-Projects/Terraform_CICD_Setup"
        ]

        for location in alt_locations:
            if os.path.exists(location):
                terraform_dir = location
                break
        else:
            raise HTTPException(status_code=404, detail="Terraform_CICD_Setup project not found")

    try:
        print(f"🎯 James scanning Terraform_CICD_Setup at: {terraform_dir}")
        results = scanner.scan_directory(terraform_dir, "Terraform_CICD_Setup")

        return {
            "message": "James scanned your Terraform_CICD_Setup project",
            "location": terraform_dir,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terraform scan failed: {str(e)}")

@app.get("/")
async def root():
    return {
        "service": "GuidePoint Security Platform - WORKING",
        "status": "operational",
        "james_scanner": "active",
        "ready_for": "Terraform_CICD_Setup scanning"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "guidepoint",
        "james": "ready",
        "scanner": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GuidePoint - Ready to scan your projects!")
    uvicorn.run(app, host="0.0.0.0", port=8080)