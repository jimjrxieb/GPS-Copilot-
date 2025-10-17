#!/usr/bin/env python3
"""
GuidePoint Client for James MLOps Models
High-performance client for GuidePoint agents to interact with james-mlops inference API
"""

import httpx
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import hashlib

@dataclass
class VulnerabilityContext:
    """Vulnerability information for model prediction"""
    type: str
    domain: str
    severity: str
    environment: str
    tool: str
    context: Dict[str, Any]

@dataclass
class FixApproach:
    """Fix approach information for model ranking"""
    type: str
    requires_restart: bool
    complexity_score: float
    steps: List[str]

@dataclass
class PredictionResult:
    """Result from confidence prediction"""
    prediction_id: str
    confidence_score: float
    confidence_interval: List[float]
    risk_factors: List[Dict[str, Any]]
    recommendation: str
    model_metadata: Dict[str, Any]

@dataclass
class ExecutionResult:
    """Execution result for feedback reporting"""
    agent_id: str
    timestamp: str
    vulnerability: Dict[str, Any]
    fix_applied: Dict[str, Any]
    outcome: Dict[str, Any]
    environment: Dict[str, Any]

class CircuitBreaker:
    """Circuit breaker for reliability"""

    def __init__(self, failure_threshold: int = 5, timeout_duration: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_duration = timeout_duration
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def is_available(self) -> bool:
        """Check if circuit breaker allows requests"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if self.last_failure_time:
                time_since_failure = datetime.now() - self.last_failure_time
                if time_since_failure.seconds > self.timeout_duration:
                    self.state = "HALF_OPEN"
                    return True
            return False
        else:  # HALF_OPEN
            return True

    def record_success(self):
        """Record successful operation"""
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

class JamesMLOpsClient:
    """
    Client for GuidePoint agents to interact with james-mlops models

    Features:
    - Async HTTP client for low latency
    - Circuit breaker for reliability
    - Local caching for performance
    - Graceful degradation when models unavailable
    - Execution result reporting for continuous learning
    """

    def __init__(self, james_mlops_url: str = "http://localhost:8006"):
        self.base_url = james_mlops_url
        self.circuit_breaker = CircuitBreaker()
        self.local_cache = {}
        self.retry_queue = []
        self.logger = logging.getLogger(__name__)

        # Performance tracking
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "fallback_uses": 0
        }

    def _generate_cache_key(self, vulnerability: Dict, fix_approach: Dict) -> str:
        """Generate cache key for prediction requests"""
        content = json.dumps({
            "vulnerability": vulnerability,
            "fix_approach": fix_approach
        }, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        cache_time = datetime.fromisoformat(cache_entry["timestamp"])
        return datetime.now() - cache_time < timedelta(hours=1)

    async def predict_confidence(
        self,
        vulnerability: VulnerabilityContext,
        fix_approach: FixApproach
    ) -> PredictionResult:
        """Get confidence prediction from james-mlops with caching and fallback"""

        self.performance_metrics["total_requests"] += 1

        # Check cache first
        cache_key = self._generate_cache_key(
            vulnerability.__dict__,
            fix_approach.__dict__
        )

        if cache_key in self.local_cache:
            cache_entry = self.local_cache[cache_key]
            if self._is_cache_valid(cache_entry):
                self.performance_metrics["cache_hits"] += 1
                return PredictionResult(**cache_entry["result"])

        # Check circuit breaker
        if not self.circuit_breaker.is_available():
            self.performance_metrics["fallback_uses"] += 1
            return self._fallback_confidence_prediction(vulnerability, fix_approach)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/models/confidence/predict",
                    json={
                        "model_version": "confidence_v2.1",
                        "vulnerability": {
                            "type": vulnerability.type,
                            "domain": vulnerability.domain,
                            "severity": vulnerability.severity,
                            "environment": vulnerability.environment,
                            "context": {
                                "tool": vulnerability.tool,
                                **vulnerability.context
                            }
                        },
                        "fix_approach": {
                            "type": fix_approach.type,
                            "requires_restart": fix_approach.requires_restart,
                            "complexity_score": fix_approach.complexity_score
                        }
                    },
                    timeout=2.0  # Fast timeout for real-time use
                )

                if response.status_code == 200:
                    result_data = response.json()

                    # Cache the result
                    self.local_cache[cache_key] = {
                        "result": result_data,
                        "timestamp": datetime.now().isoformat()
                    }

                    self.circuit_breaker.record_success()
                    self.performance_metrics["successful_requests"] += 1

                    return PredictionResult(
                        prediction_id=result_data["prediction_id"],
                        confidence_score=result_data["confidence_score"],
                        confidence_interval=result_data["confidence_interval"],
                        risk_factors=result_data["risk_factors"],
                        recommendation=result_data["recommendation"],
                        model_metadata=result_data["model_metadata"]
                    )
                else:
                    self.circuit_breaker.record_failure()
                    self.performance_metrics["failed_requests"] += 1
                    self.performance_metrics["fallback_uses"] += 1
                    return self._fallback_confidence_prediction(vulnerability, fix_approach)

        except Exception as e:
            self.logger.warning(f"Model prediction failed: {e}")
            self.circuit_breaker.record_failure()
            self.performance_metrics["failed_requests"] += 1
            self.performance_metrics["fallback_uses"] += 1
            return self._fallback_confidence_prediction(vulnerability, fix_approach)

    def _fallback_confidence_prediction(
        self,
        vulnerability: VulnerabilityContext,
        fix_approach: FixApproach
    ) -> PredictionResult:
        """Fallback confidence prediction when models unavailable"""

        # Use heuristics based on vulnerability and fix characteristics
        base_confidence = 0.5

        # Adjust based on severity
        severity_adjustments = {
            "HIGH": -0.1,  # More conservative for high severity
            "MEDIUM": 0.0,
            "LOW": 0.1,
            "INFO": 0.2
        }
        base_confidence += severity_adjustments.get(vulnerability.severity, 0.0)

        # Adjust based on environment
        if vulnerability.environment == "production":
            base_confidence -= 0.1
        elif vulnerability.environment == "development":
            base_confidence += 0.1

        # Adjust based on fix complexity
        if fix_approach.complexity_score > 0.7:
            base_confidence -= 0.2
        elif fix_approach.complexity_score < 0.3:
            base_confidence += 0.1

        # Adjust based on restart requirement
        if fix_approach.requires_restart:
            base_confidence -= 0.1

        # Clamp to valid range
        confidence = max(0.1, min(0.9, base_confidence))

        return PredictionResult(
            prediction_id=f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            confidence_score=confidence,
            confidence_interval=[confidence - 0.1, confidence + 0.1],
            risk_factors=[{
                "factor": "fallback_mode",
                "impact": 0.0,
                "description": "Using heuristic-based confidence due to model unavailability"
            }],
            recommendation="MODERATE_CONFIDENCE",
            model_metadata={
                "model_version": "fallback_heuristics_v1.0",
                "fallback_mode": True,
                "heuristic_factors": {
                    "severity": vulnerability.severity,
                    "environment": vulnerability.environment,
                    "complexity": fix_approach.complexity_score
                }
            }
        )

    async def rank_fix_options(
        self,
        vulnerability: VulnerabilityContext,
        fix_options: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Get ranked fix options from james-mlops"""

        if not self.circuit_breaker.is_available():
            return self._fallback_fix_ranking(vulnerability, fix_options)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/models/fix_selection/rank",
                    json={
                        "vulnerability": vulnerability.__dict__,
                        "fix_options": fix_options
                    },
                    timeout=2.0
                )

                if response.status_code == 200:
                    result = response.json()
                    self.circuit_breaker.record_success()
                    return result["ranked_fixes"]
                else:
                    self.circuit_breaker.record_failure()
                    return self._fallback_fix_ranking(vulnerability, fix_options)

        except Exception as e:
            self.logger.warning(f"Fix ranking failed: {e}")
            self.circuit_breaker.record_failure()
            return self._fallback_fix_ranking(vulnerability, fix_options)

    def _fallback_fix_ranking(
        self,
        vulnerability: VulnerabilityContext,
        fix_options: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Fallback fix ranking using simple heuristics"""

        ranked_fixes = []
        for fix in fix_options:
            # Simple scoring based on complexity and safety
            effectiveness_score = 0.7  # Default moderate effectiveness

            # Prefer simpler fixes
            if fix.get("complexity", 0.5) < 0.3:
                effectiveness_score += 0.1
            elif fix.get("complexity", 0.5) > 0.7:
                effectiveness_score -= 0.1

            # Prefer fixes that don't require restarts
            if not fix.get("requires_restart", False):
                effectiveness_score += 0.05

            ranked_fixes.append({
                "fix_id": fix.get("id", "unknown"),
                "effectiveness_score": effectiveness_score,
                "confidence": 0.6,  # Moderate confidence for fallback
                "reasoning": "Fallback heuristic ranking - prefer simple, safe fixes"
            })

        # Sort by effectiveness score
        ranked_fixes.sort(key=lambda x: x["effectiveness_score"], reverse=True)
        return ranked_fixes

    async def report_execution_result(
        self,
        prediction_id: str,
        execution_result: ExecutionResult
    ) -> bool:
        """Report execution result back to james-mlops for learning"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/training/execution_result",
                    json={
                        "prediction_id": prediction_id,
                        "execution": {
                            "agent_id": execution_result.agent_id,
                            "timestamp": execution_result.timestamp,
                            "vulnerability": execution_result.vulnerability,
                            "fix_applied": execution_result.fix_applied,
                            "outcome": execution_result.outcome,
                            "environment": execution_result.environment
                        }
                    },
                    timeout=5.0  # Longer timeout for training data
                )

                if response.status_code == 200:
                    self.logger.info(f"Execution result reported: {prediction_id}")
                    return True
                else:
                    self.logger.warning(f"Failed to report execution result: {response.status_code}")
                    self._queue_for_retry(prediction_id, execution_result)
                    return False

        except Exception as e:
            self.logger.warning(f"Failed to report execution result: {e}")
            self._queue_for_retry(prediction_id, execution_result)
            return False

    def _queue_for_retry(self, prediction_id: str, execution_result: ExecutionResult):
        """Queue execution result for retry later"""
        self.retry_queue.append({
            "prediction_id": prediction_id,
            "execution_result": execution_result,
            "retry_count": 0,
            "queued_at": datetime.now()
        })

    async def process_retry_queue(self):
        """Process queued execution results for retry"""
        if not self.retry_queue:
            return

        successful_reports = []
        for i, queued_item in enumerate(self.retry_queue):
            if queued_item["retry_count"] < 3:  # Max 3 retries
                success = await self.report_execution_result(
                    queued_item["prediction_id"],
                    queued_item["execution_result"]
                )

                if success:
                    successful_reports.append(i)
                else:
                    queued_item["retry_count"] += 1

        # Remove successfully reported items
        for i in reversed(successful_reports):
            del self.retry_queue[i]

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get client performance metrics"""
        total_requests = self.performance_metrics["total_requests"]
        if total_requests == 0:
            return self.performance_metrics

        return {
            **self.performance_metrics,
            "success_rate": self.performance_metrics["successful_requests"] / total_requests,
            "cache_hit_rate": self.performance_metrics["cache_hits"] / total_requests,
            "fallback_rate": self.performance_metrics["fallback_uses"] / total_requests,
            "circuit_breaker_state": self.circuit_breaker.state
        }

    async def health_check(self) -> Dict[str, Any]:
        """Check health of james-mlops service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    timeout=5.0
                )

                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "response_time": response.elapsed.total_seconds(),
                        "service_info": response.json()
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "status_code": response.status_code
                    }

        except Exception as e:
            return {
                "status": "unreachable",
                "error": str(e)
            }

# Convenience functions for GuidePoint agents
async def get_fix_confidence(
    vulnerability_type: str,
    severity: str,
    environment: str,
    fix_complexity: float,
    requires_restart: bool = False,
    client: Optional[JamesMLOpsClient] = None
) -> float:
    """Convenience function to get fix confidence"""

    if client is None:
        client = JamesMLOpsClient()

    vulnerability = VulnerabilityContext(
        type=vulnerability_type,
        domain="security",
        severity=severity,
        environment=environment,
        tool="guidepoint",
        context={}
    )

    fix_approach = FixApproach(
        type="automated_fix",
        requires_restart=requires_restart,
        complexity_score=fix_complexity,
        steps=[]
    )

    result = await client.predict_confidence(vulnerability, fix_approach)
    return result.confidence_score

async def report_fix_outcome(
    agent_id: str,
    vulnerability_details: Dict[str, Any],
    fix_details: Dict[str, Any],
    success: bool,
    execution_time: float,
    issues: List[str] = None,
    client: Optional[JamesMLOpsClient] = None
) -> bool:
    """Convenience function to report fix outcome"""

    if client is None:
        client = JamesMLOpsClient()

    execution_result = ExecutionResult(
        agent_id=agent_id,
        timestamp=datetime.now().isoformat(),
        vulnerability=vulnerability_details,
        fix_applied=fix_details,
        outcome={
            "success": success,
            "execution_time": execution_time,
            "issues_encountered": issues or [],
            "post_scan_results": {
                "vulnerability_resolved": success,
                "new_issues_introduced": len(issues or []) > 0
            }
        },
        environment={
            "type": "guidepoint_execution",
            "timestamp": datetime.now().isoformat()
        }
    )

    return await client.report_execution_result("", execution_result)

if __name__ == "__main__":
    # Example usage and testing
    async def test_client():
        client = JamesMLOpsClient()

        # Test health check
        health = await client.health_check()
        print(f"Health check: {health}")

        # Test confidence prediction
        confidence = await get_fix_confidence(
            vulnerability_type="k8s-TRIVY-013",
            severity="HIGH",
            environment="production",
            fix_complexity=0.3
        )
        print(f"Confidence prediction: {confidence}")

        # Test performance metrics
        metrics = client.get_performance_metrics()
        print(f"Performance metrics: {metrics}")

    asyncio.run(test_client())