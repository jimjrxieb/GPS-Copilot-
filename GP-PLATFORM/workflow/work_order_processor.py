#!/usr/bin/env python3
"""
James-OS Work Order Processor
Autonomous workflow management for security operations

This script monitors the inbox for new work orders and routes them based on
confidence levels and task complexity.
"""

import os
import json
import yaml
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import aiofiles
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('james-workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('james-workflow')

class TaskType(Enum):
    SECURITY_ASSESSMENT = "security_assessment"
    INCIDENT_RESPONSE = "incident_response"
    VULNERABILITY_SCAN = "vulnerability_scan"
    COMPLIANCE_AUDIT = "compliance_audit"
    PENETRATION_TEST = "penetration_test"
    CODE_REVIEW = "code_review"

class ConfidenceLevel(Enum):
    HIGH = "high"      # 95%+ - Full autonomous execution
    MEDIUM = "medium"  # 80-94% - Supervised execution
    LOW = "low"       # <80% - Human review required

class WorkOrderStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_HUMAN = "requires_human"

@dataclass
class WorkOrder:
    """Work order data structure"""
    id: str
    task_type: TaskType
    title: str
    description: str
    client: str
    priority: str  # P1, P2, P3, P4
    target_systems: List[str]
    business_context: str
    created_at: datetime
    due_date: datetime
    assigned_to: str = "james-os"
    status: WorkOrderStatus = WorkOrderStatus.PENDING
    confidence_level: Optional[ConfidenceLevel] = None
    evidence_hash: Optional[str] = None
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    scan_results: List[Dict] = None

    def __post_init__(self):
        if self.scan_results is None:
            self.scan_results = []

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        # Convert datetime objects to ISO strings
        result['created_at'] = self.created_at.isoformat()
        result['due_date'] = self.due_date.isoformat()
        # Convert enums to strings
        result['task_type'] = self.task_type.value
        result['status'] = self.status.value
        if self.confidence_level:
            result['confidence_level'] = self.confidence_level.value
        return result

class JamesWorkflowEngine:
    """Autonomous workflow processing engine"""

    def __init__(self):
        self.base_path = Path("sync")
        self.inbox_path = self.base_path / "inbox"
        self.active_path = self.base_path / "active-projects"
        self.completed_path = self.base_path / "completed-work"
        self.templates_path = self.base_path / "templates"
        self.learning_path = self.base_path / "learning-data"

        # James-OS service endpoints
        self.ms_brain_url = "http://localhost:8001"
        self.ms_agents_url = "http://localhost:8006"

        # Confidence scoring database
        self.confidence_db = {}
        self._load_confidence_data()

    def _load_confidence_data(self):
        """Load historical confidence scores for pattern matching"""
        confidence_file = self.learning_path / "confidence_scores.json"
        if confidence_file.exists():
            with open(confidence_file, 'r') as f:
                self.confidence_db = json.load(f)

        # Default confidence patterns
        if not self.confidence_db:
            self.confidence_db = {
                "vulnerability_scan": {"base_confidence": 0.95, "success_rate": 0.98},
                "security_assessment": {"base_confidence": 0.90, "success_rate": 0.92},
                "incident_response": {"base_confidence": 0.75, "success_rate": 0.88},
                "compliance_audit": {"base_confidence": 0.85, "success_rate": 0.91},
                "penetration_test": {"base_confidence": 0.65, "success_rate": 0.78},
                "code_review": {"base_confidence": 0.80, "success_rate": 0.85}
            }

    def calculate_confidence(self, work_order: WorkOrder) -> ConfidenceLevel:
        """Calculate confidence level for autonomous execution"""
        task_key = work_order.task_type.value
        base_confidence = self.confidence_db.get(task_key, {}).get("base_confidence", 0.7)

        # Adjust confidence based on various factors
        confidence_score = base_confidence

        # Priority adjustment
        if work_order.priority == "P1":
            confidence_score *= 0.9  # Be more conservative on critical issues
        elif work_order.priority == "P4":
            confidence_score *= 1.1  # Higher confidence on low priority

        # Client familiarity (simulate learning)
        if work_order.client in ["portfolio", "internal", "test"]:
            confidence_score *= 1.05  # Higher confidence on familiar systems

        # Target system complexity
        if len(work_order.target_systems) > 5:
            confidence_score *= 0.95  # Lower confidence on complex environments

        # Convert to confidence level
        if confidence_score >= 0.95:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 0.80:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    async def process_inbox(self):
        """Monitor and process new work orders from inbox"""
        logger.info("Processing inbox for new work orders...")

        for work_file in self.inbox_path.glob("*.yaml"):
            try:
                await self._process_work_order_file(work_file)
            except Exception as e:
                logger.error(f"Failed to process {work_file}: {e}")

    async def _process_work_order_file(self, work_file: Path):
        """Process individual work order file"""
        logger.info(f"Processing work order: {work_file.name}")

        # Load work order
        with open(work_file, 'r') as f:
            data = yaml.safe_load(f)

        work_order = self._create_work_order_from_dict(data)

        # Calculate confidence level
        work_order.confidence_level = self.calculate_confidence(work_order)

        # Create active project directory first
        active_dir = self.active_path / work_order.id
        active_dir.mkdir(parents=True, exist_ok=True)

        # Route based on confidence level
        if work_order.confidence_level == ConfidenceLevel.HIGH:
            await self._execute_autonomous_workflow(work_order)
        elif work_order.confidence_level == ConfidenceLevel.MEDIUM:
            await self._execute_supervised_workflow(work_order)
        else:
            await self._route_to_human_review(work_order)

        # Save work order with confidence level
        work_order_file = active_dir / "work_order.json"
        with open(work_order_file, 'w') as f:
            json.dump(work_order.to_dict(), f, indent=2)

        # Remove from inbox
        work_file.unlink()

        logger.info(f"Work order {work_order.id} routed with {work_order.confidence_level.value} confidence")

    def _create_work_order_from_dict(self, data: Dict) -> WorkOrder:
        """Create WorkOrder object from dictionary"""
        return WorkOrder(
            id=data.get('id', self._generate_work_order_id()),
            task_type=TaskType(data['task_type']),
            title=data['title'],
            description=data['description'],
            client=data['client'],
            priority=data.get('priority', 'P3'),
            target_systems=data['target_systems'],
            business_context=data['business_context'],
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            due_date=datetime.fromisoformat(data.get('due_date', (datetime.now() + timedelta(days=7)).isoformat()))
        )

    def _generate_work_order_id(self) -> str:
        """Generate unique work order ID"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        random_suffix = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:6]
        return f"WO-{timestamp}-{random_suffix}"

    async def _execute_autonomous_workflow(self, work_order: WorkOrder):
        """Execute workflow with full autonomy (95%+ confidence)"""
        logger.info(f"Executing autonomous workflow for {work_order.id}")
        work_order.status = WorkOrderStatus.IN_PROGRESS

        try:
            if work_order.task_type == TaskType.SECURITY_ASSESSMENT:
                await self._autonomous_security_assessment(work_order)
            elif work_order.task_type == TaskType.VULNERABILITY_SCAN:
                await self._autonomous_vulnerability_scan(work_order)
            # Add other task types as needed

            work_order.status = WorkOrderStatus.COMPLETED
            await self._move_to_completed(work_order)

        except Exception as e:
            logger.error(f"Autonomous workflow failed for {work_order.id}: {e}")
            work_order.status = WorkOrderStatus.FAILED

    async def _execute_supervised_workflow(self, work_order: WorkOrder):
        """Execute workflow with human supervision (80-94% confidence)"""
        logger.info(f"Executing supervised workflow for {work_order.id}")
        work_order.status = WorkOrderStatus.IN_PROGRESS

        # Execute work with checkpoints for human review
        await self._create_supervision_checkpoints(work_order)

    async def _route_to_human_review(self, work_order: WorkOrder):
        """Route work order to human review (<80% confidence)"""
        logger.info(f"Routing {work_order.id} to human review - confidence too low")
        work_order.status = WorkOrderStatus.REQUIRES_HUMAN

        # Create human review request
        await self._create_human_review_request(work_order)

    async def _autonomous_security_assessment(self, work_order: WorkOrder):
        """Execute autonomous security assessment"""
        logger.info(f"Starting autonomous security assessment for {work_order.id}")

        # Call James-OS security assessment API
        payload = {
            "target_organization": work_order.client,
            "target_systems": work_order.target_systems,
            "business_context": work_order.business_context
        }

        # Simulate API call (replace with actual implementation)
        response = await self._call_james_security_api(payload)

        # Generate assessment report
        await self._generate_assessment_report(work_order, response)

    async def _autonomous_vulnerability_scan(self, work_order: WorkOrder):
        """Execute autonomous vulnerability scan"""
        logger.info(f"Starting autonomous vulnerability scan for {work_order.id}")

        scan_results = []
        for target in work_order.target_systems:
            # Execute Trivy scan (real implementation)
            trivy_result = await self._run_trivy_scan(target)
            scan_results.append(trivy_result)

        # Store scan results for report generation
        work_order.scan_results = scan_results

        # Generate report with real data
        await self._generate_vulnerability_report(work_order)

    async def _call_james_security_api(self, payload: Dict) -> Dict:
        """Call James-OS security assessment API"""
        try:
            # This would be the actual API call to ms-agents
            # For now, return simulated success
            return {"status": "completed", "findings_count": 12, "critical_issues": 3}
        except Exception as e:
            logger.error(f"Failed to call James security API: {e}")
            raise

    async def _run_trivy_scan(self, target: str) -> Dict:
        """Run Trivy container security scan"""
        logger.info(f"Running Trivy scan on {target}")

        try:
            import subprocess
            import tempfile

            # Create temp file for output
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as f:
                output_file = f.name

            # Run trivy scan with JSON output
            cmd = [
                "./bin/trivy", "fs", target,
                "--format", "json",
                "--output", output_file,
                "--quiet"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                # Read and parse results
                with open(output_file, 'r') as f:
                    scan_results = json.load(f)

                # Clean up temp file
                os.unlink(output_file)

                # Extract key metrics
                total_vulns = 0
                critical_count = 0
                high_count = 0

                if 'Results' in scan_results:
                    for result in scan_results['Results']:
                        if 'Vulnerabilities' in result:
                            for vuln in result['Vulnerabilities']:
                                total_vulns += 1
                                severity = vuln.get('Severity', '').upper()
                                if severity == 'CRITICAL':
                                    critical_count += 1
                                elif severity == 'HIGH':
                                    high_count += 1

                logger.info(f"Trivy scan completed: {total_vulns} vulnerabilities found")
                return {
                    "status": "completed",
                    "target": target,
                    "total_vulnerabilities": total_vulns,
                    "critical": critical_count,
                    "high": high_count,
                    "raw_results": scan_results
                }
            else:
                logger.error(f"Trivy scan failed: {result.stderr}")
                return {"status": "failed", "error": result.stderr}

        except Exception as e:
            logger.error(f"Trivy scan exception: {e}")
            return {"status": "failed", "error": str(e)}

    async def _run_checkov_scan(self, target: str):
        """Run Checkov infrastructure scan"""
        logger.info(f"Running Checkov scan on {target}")
        # Implementation would call actual Checkov scanner
        pass

    async def _run_nuclei_scan(self, target: str):
        """Run Nuclei web vulnerability scan"""
        logger.info(f"Running Nuclei scan on {target}")
        # Implementation would call actual Nuclei scanner
        pass

    async def _generate_assessment_report(self, work_order: WorkOrder, results: Dict):
        """Generate professional security assessment report"""
        report_path = self.active_path / work_order.id / "security_assessment_report.md"

        # Use template and populate with results
        template_path = self.templates_path / "security-assessment-template.md"

        with open(template_path, 'r') as f:
            template = f.read()

        # Replace template variables (simplified)
        report_content = template.replace("[CLIENT_NAME]", work_order.client)
        report_content = report_content.replace("[DATE]", datetime.now().strftime("%Y-%m-%d"))

        with open(report_path, 'w') as f:
            f.write(report_content)

        logger.info(f"Generated assessment report for {work_order.id}")

    async def _generate_vulnerability_report(self, work_order: WorkOrder):
        """Generate vulnerability scan report with real scan data"""
        logger.info(f"Generating vulnerability report for {work_order.id}")

        report_path = self.active_path / work_order.id / "vulnerability_scan_report.md"

        # Aggregate scan results
        total_vulns = 0
        critical_count = 0
        high_count = 0
        scan_summary = []

        for result in work_order.scan_results:
            if result["status"] == "completed":
                total_vulns += result["total_vulnerabilities"]
                critical_count += result["critical"]
                high_count += result["high"]
                scan_summary.append(f"- **{result['target']}**: {result['total_vulnerabilities']} vulnerabilities ({result['critical']} critical, {result['high']} high)")

        # Generate report content
        report_content = f"""# Vulnerability Scan Report
**James-OS Autonomous Security Assessment**

## Executive Summary
- **Assessment ID**: {work_order.id}
- **Client**: {work_order.client}
- **Scan Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total Vulnerabilities**: {total_vulns}
- **Critical Issues**: {critical_count}
- **High Severity**: {high_count}

## Scan Results by Target
{chr(10).join(scan_summary)}

## Risk Assessment
- **Risk Level**: {"HIGH" if critical_count > 0 else "MEDIUM" if high_count > 0 else "LOW"}
- **Immediate Action Required**: {"YES" if critical_count > 0 else "NO"}

## Tools Used
- **Trivy**: Container and filesystem vulnerability scanner
- **Scan Duration**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Next Steps
{"- [ ] Address critical vulnerabilities immediately" if critical_count > 0 else ""}
{"- [ ] Review high severity findings" if high_count > 0 else ""}
- [ ] Schedule follow-up scan in 30 days

---
*Generated by James-OS Autonomous Security Platform*
"""

        with open(report_path, 'w') as f:
            f.write(report_content)

        logger.info(f"Vulnerability report generated: {report_path}")

        # Save raw scan data
        raw_data_path = self.active_path / work_order.id / "raw_scan_data.json"
        with open(raw_data_path, 'w') as f:
            json.dump(work_order.scan_results, f, indent=2)

        logger.info(f"Raw scan data saved: {raw_data_path}")

    async def _create_supervision_checkpoints(self, work_order: WorkOrder):
        """Create checkpoints for human supervision"""
        checkpoints_file = self.active_path / work_order.id / "supervision_checkpoints.json"

        checkpoints = {
            "work_order_id": work_order.id,
            "checkpoints": [
                {"stage": "planning", "status": "pending", "requires_approval": True},
                {"stage": "execution", "status": "pending", "requires_approval": False},
                {"stage": "validation", "status": "pending", "requires_approval": True},
                {"stage": "delivery", "status": "pending", "requires_approval": True}
            ],
            "created_at": datetime.now().isoformat()
        }

        with open(checkpoints_file, 'w') as f:
            json.dump(checkpoints, f, indent=2)

    async def _create_human_review_request(self, work_order: WorkOrder):
        """Create human review request"""
        review_file = self.active_path / work_order.id / "human_review_required.json"

        review_request = {
            "work_order_id": work_order.id,
            "reason": "Confidence level below autonomous threshold",
            "confidence_level": work_order.confidence_level.value,
            "recommended_approach": "Manual assessment with James-OS assistance",
            "escalation_level": "Senior Security Engineer",
            "created_at": datetime.now().isoformat()
        }

        with open(review_file, 'w') as f:
            json.dump(review_request, f, indent=2)

    async def _move_to_completed(self, work_order: WorkOrder):
        """Move completed work order to completed-work directory"""
        source_dir = self.active_path / work_order.id
        dest_dir = self.completed_path / f"{datetime.now().strftime('%Y-%m-%d')}-{work_order.id}"

        # Move directory
        source_dir.rename(dest_dir)

        # Update learning data
        await self._update_learning_data(work_order, success=True)

        logger.info(f"Work order {work_order.id} moved to completed work")

    async def _update_learning_data(self, work_order: WorkOrder, success: bool):
        """Update learning data for confidence scoring"""
        task_key = work_order.task_type.value

        if task_key in self.confidence_db:
            current_rate = self.confidence_db[task_key]["success_rate"]
            # Simple exponential moving average
            alpha = 0.1
            new_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * current_rate
            self.confidence_db[task_key]["success_rate"] = new_rate

        # Save updated confidence data
        confidence_file = self.learning_path / "confidence_scores.json"
        with open(confidence_file, 'w') as f:
            json.dump(self.confidence_db, f, indent=2)

async def main():
    """Main workflow processing loop"""
    workflow_engine = JamesWorkflowEngine()

    logger.info("James-OS Work Order Processor started")

    while True:
        try:
            await workflow_engine.process_inbox()
            await asyncio.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            logger.info("Workflow processor stopped by user")
            break
        except Exception as e:
            logger.error(f"Workflow processor error: {e}")
            await asyncio.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    asyncio.run(main())