#!/usr/bin/env python3
"""
Jade Evidence Logger
Append-only JSONL logging for all Jade actions
Provides complete observability and auditability
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib
from contextlib import contextmanager


class JadeLogger:
    """
    Append-only evidence logger for Jade
    All actions logged to ~/.jade/evidence.jsonl
    """

    def __init__(self, log_path: Optional[Path] = None):
        """
        Initialize Jade logger

        Args:
            log_path: Custom log path (defaults to ~/.jade/evidence.jsonl)
        """
        if log_path:
            self.log_path = Path(log_path)
        else:
            self.log_path = Path.home() / ".jade" / "evidence.jsonl"

        # Ensure directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Create file if it doesn't exist
        if not self.log_path.exists():
            self.log_path.touch()
            self._log_system_event("logger_initialized", {
                "log_path": str(self.log_path),
                "created": True
            })

    def log_action(
        self,
        action: str,
        target: str,
        findings: Optional[int] = None,
        llm_confidence: Optional[float] = None,
        fix_proposed: bool = False,
        fix_valid: Optional[bool] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log a Jade action with full context

        Args:
            action: Action type (scan, fix, analyze, query, etc.)
            target: Target of action (file path, project, query text)
            findings: Number of findings/issues detected
            llm_confidence: LLM confidence score (0.0-1.0)
            fix_proposed: Whether a fix was proposed
            fix_valid: Whether the proposed fix validated successfully
            metadata: Additional metadata (scanner used, severity breakdown, etc.)
            error: Error message if action failed

        Returns:
            The logged event dict
        """
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": action,
            "target": target,
        }

        # Add optional fields
        if findings is not None:
            event["findings"] = findings

        if llm_confidence is not None:
            event["llm_confidence"] = round(llm_confidence, 3)

        if fix_proposed:
            event["fix_proposed"] = fix_proposed

        if fix_valid is not None:
            event["fix_valid"] = fix_valid

        if error:
            event["error"] = error
            event["status"] = "failed"
        else:
            event["status"] = "success"

        if metadata:
            event["metadata"] = metadata

        # Add event hash for tamper detection
        event["event_hash"] = self._compute_hash(event)

        # Append to JSONL file
        self._append_event(event)

        return event

    def log_scan(
        self,
        scanner: str,
        target: str,
        findings: int,
        severity_breakdown: Optional[Dict[str, int]] = None,
        scan_duration_seconds: Optional[float] = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log a scanner execution"""
        metadata = {
            "scanner": scanner,
            "severity_breakdown": severity_breakdown or {}
        }

        if scan_duration_seconds is not None:
            metadata["scan_duration_seconds"] = round(scan_duration_seconds, 2)

        return self.log_action(
            action="scan",
            target=target,
            findings=findings,
            metadata=metadata,
            error=error
        )

    def log_fix(
        self,
        fixer: str,
        target: str,
        issues_fixed: int,
        fix_valid: bool,
        llm_used: bool = False,
        llm_confidence: Optional[float] = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log a fixer execution"""
        metadata = {
            "fixer": fixer,
            "issues_fixed": issues_fixed,
            "llm_used": llm_used
        }

        return self.log_action(
            action="fix",
            target=target,
            fix_proposed=True,
            fix_valid=fix_valid,
            llm_confidence=llm_confidence if llm_used else None,
            metadata=metadata,
            error=error
        )

    def log_llm_query(
        self,
        query: str,
        model: str,
        response_length: int,
        confidence: Optional[float] = None,
        rag_used: bool = False,
        rag_results_count: Optional[int] = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log an LLM query"""
        metadata = {
            "model": model,
            "response_length": response_length,
            "rag_used": rag_used,
            "query_hash": hashlib.sha256(query.encode()).hexdigest()[:16]
        }

        if rag_used and rag_results_count is not None:
            metadata["rag_results_count"] = rag_results_count

        return self.log_action(
            action="llm_query",
            target=query[:100],  # Truncate long queries
            llm_confidence=confidence,
            metadata=metadata,
            error=error
        )

    def log_workflow(
        self,
        workflow_name: str,
        target: str,
        steps_completed: int,
        steps_total: int,
        success: bool,
        duration_seconds: Optional[float] = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log a workflow execution"""
        metadata = {
            "workflow": workflow_name,
            "steps_completed": steps_completed,
            "steps_total": steps_total,
            "completion_rate": round(steps_completed / steps_total * 100, 1) if steps_total > 0 else 0
        }

        if duration_seconds is not None:
            metadata["duration_seconds"] = round(duration_seconds, 2)

        return self.log_action(
            action="workflow",
            target=target,
            metadata=metadata,
            error=error if not success else None
        )

    def log_user_interaction(
        self,
        interaction_type: str,
        user_input: str,
        jade_response: str,
        satisfaction: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log user interaction for learning"""
        metadata = {
            "interaction_type": interaction_type,
            "user_input_length": len(user_input),
            "response_length": len(jade_response),
            "input_hash": hashlib.sha256(user_input.encode()).hexdigest()[:16]
        }

        if satisfaction:
            metadata["user_satisfaction"] = satisfaction

        return self.log_action(
            action="user_interaction",
            target=user_input[:100],
            metadata=metadata
        )

    @contextmanager
    def action_context(self, action: str, target: str, **kwargs):
        """
        Context manager for tracking action start/end with timing

        Usage:
            with logger.action_context("scan", "my-project") as ctx:
                # Do scan work
                ctx.update(findings=10)
        """
        start_time = datetime.utcnow()
        context = {"metadata": kwargs.get("metadata", {})}

        def update(**updates):
            context.update(updates)

        context["update"] = update

        try:
            yield context
            duration = (datetime.utcnow() - start_time).total_seconds()
            context.setdefault("metadata", {})["duration_seconds"] = round(duration, 2)
            self.log_action(action=action, target=target, **{k: v for k, v in context.items() if k != "update"})

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            context.setdefault("metadata", {})["duration_seconds"] = round(duration, 2)
            self.log_action(action=action, target=target, error=str(e), **{k: v for k, v in context.items() if k != "update"})
            raise

    def get_recent_events(self, limit: int = 100) -> list:
        """Get recent events from log"""
        events = []

        if not self.log_path.exists():
            return events

        with open(self.log_path, 'r') as f:
            lines = f.readlines()
            # Get last N lines
            for line in lines[-limit:]:
                if line.strip():
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

        return events

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from evidence log"""
        events = self.get_recent_events(limit=10000)  # Last 10k events

        if not events:
            return {
                "total_events": 0,
                "actions": {},
                "error_rate": 0,
                "avg_llm_confidence": None
            }

        stats = {
            "total_events": len(events),
            "actions": {},
            "errors": 0,
            "llm_queries": 0,
            "total_findings": 0,
            "fixes_proposed": 0,
            "fixes_valid": 0,
            "llm_confidences": []
        }

        for event in events:
            action = event.get("action", "unknown")
            stats["actions"][action] = stats["actions"].get(action, 0) + 1

            if event.get("error"):
                stats["errors"] += 1

            if event.get("findings"):
                stats["total_findings"] += event["findings"]

            if event.get("fix_proposed"):
                stats["fixes_proposed"] += 1

            if event.get("fix_valid"):
                stats["fixes_valid"] += 1

            if event.get("llm_confidence"):
                stats["llm_confidences"].append(event["llm_confidence"])

        stats["error_rate"] = round(stats["errors"] / len(events) * 100, 2) if events else 0
        stats["avg_llm_confidence"] = round(sum(stats["llm_confidences"]) / len(stats["llm_confidences"]), 3) if stats["llm_confidences"] else None
        stats["fix_success_rate"] = round(stats["fixes_valid"] / stats["fixes_proposed"] * 100, 2) if stats["fixes_proposed"] > 0 else None

        return stats

    def _append_event(self, event: Dict[str, Any]):
        """Append event to JSONL file (append-only)"""
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(event) + '\n')

    def _compute_hash(self, event: Dict[str, Any]) -> str:
        """Compute SHA256 hash of event (excluding hash field itself)"""
        event_copy = {k: v for k, v in event.items() if k != "event_hash"}
        event_str = json.dumps(event_copy, sort_keys=True)
        return hashlib.sha256(event_str.encode()).hexdigest()[:16]

    def _log_system_event(self, event_type: str, data: Dict[str, Any]):
        """Log internal system event"""
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": "system",
            "event_type": event_type,
            "data": data
        }
        self._append_event(event)

    def verify_integrity(self) -> Dict[str, Any]:
        """Verify log file integrity by checking hashes"""
        events = self.get_recent_events(limit=10000)

        total = len(events)
        valid = 0
        invalid = []

        for i, event in enumerate(events):
            if "event_hash" in event:
                expected_hash = self._compute_hash(event)
                if expected_hash == event["event_hash"]:
                    valid += 1
                else:
                    invalid.append({
                        "line": i + 1,
                        "expected": expected_hash,
                        "actual": event["event_hash"]
                    })

        return {
            "total_events": total,
            "valid_events": valid,
            "invalid_events": len(invalid),
            "integrity_rate": round(valid / total * 100, 2) if total > 0 else 100,
            "tampered": invalid
        }


# Singleton instance
_logger_instance = None


def get_logger(log_path: Optional[Path] = None) -> JadeLogger:
    """Get singleton logger instance"""
    global _logger_instance

    if _logger_instance is None:
        _logger_instance = JadeLogger(log_path)

    return _logger_instance


# Convenience functions
def log_scan(scanner: str, target: str, findings: int, **kwargs):
    """Quick access to log_scan"""
    return get_logger().log_scan(scanner, target, findings, **kwargs)


def log_fix(fixer: str, target: str, issues_fixed: int, fix_valid: bool, **kwargs):
    """Quick access to log_fix"""
    return get_logger().log_fix(fixer, target, issues_fixed, fix_valid, **kwargs)


def log_llm_query(query: str, model: str, response_length: int, **kwargs):
    """Quick access to log_llm_query"""
    return get_logger().log_llm_query(query, model, response_length, **kwargs)


# Example usage
if __name__ == "__main__":
    # Initialize logger
    logger = JadeLogger()

    print(f"📝 Jade Evidence Logger")
    print(f"   Log file: {logger.log_path}\n")

    # Example: Log a scan
    logger.log_scan(
        scanner="bandit",
        target="GP-PROJECTS/LinkOps-MLOps",
        findings=110,
        severity_breakdown={"HIGH": 3, "MEDIUM": 11, "LOW": 96},
        scan_duration_seconds=12.5
    )
    print("✅ Logged scan action")

    # Example: Log a fix
    logger.log_fix(
        fixer="bandit_fixer",
        target="GP-PROJECTS/LinkOps-MLOps/app.py:45",
        issues_fixed=1,
        fix_valid=True,
        llm_used=True,
        llm_confidence=0.92
    )
    print("✅ Logged fix action")

    # Example: Log LLM query
    logger.log_llm_query(
        query="Explain SQL injection vulnerability",
        model="qwen2.5-7b",
        response_length=234,
        confidence=0.88,
        rag_used=True,
        rag_results_count=5
    )
    print("✅ Logged LLM query")

    # Example: Context manager
    with logger.action_context("workflow", "scan-and-fix") as ctx:
        # Simulate work
        import time
        time.sleep(0.5)
        ctx.update(findings=10, fix_proposed=True, fix_valid=True)

    print("✅ Logged workflow with timing\n")

    # Show stats
    stats = logger.get_stats()
    print("📊 Evidence Log Stats:")
    print(f"   Total events: {stats['total_events']}")
    print(f"   Actions: {stats['actions']}")
    print(f"   Error rate: {stats['error_rate']}%")
    print(f"   Avg LLM confidence: {stats['avg_llm_confidence']}")

    # Verify integrity
    print("\n🔒 Verifying log integrity...")
    integrity = logger.verify_integrity()
    print(f"   Valid events: {integrity['valid_events']}/{integrity['total_events']}")
    print(f"   Integrity: {integrity['integrity_rate']}%")

    print(f"\n📄 View log: cat {logger.log_path}")