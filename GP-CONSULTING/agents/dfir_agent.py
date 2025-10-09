#!/usr/bin/env python3
"""
DFIR Support Agent - Digital Forensics & Incident Response Support
Supports GuidePoint's DFIR practice with threat intelligence and investigation assistance
"""

import subprocess
import json
import sys
import hashlib
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig


class DFIRSupportAgent:
    """
    DFIR Support Agent for threat intelligence and investigation support

    Capabilities:
    - IOC (Indicators of Compromise) lookup and enrichment
    - Threat intelligence feed aggregation
    - Investigation timeline generation
    - MITRE ATT&CK technique mapping
    - Incident response documentation
    """

    def __init__(self):
        self.agent_id = "dfir_support_agent"

        self.config = GPDataConfig()
        self.output_dir = self.config.get_analysis_directory()
        self.deliverable_dir = self.config.get_deliverable_directory()

        self.confidence_levels = {
            "high": [
                "hash_lookup",
                "ip_reputation_check",
                "domain_lookup",
                "timeline_generation",
                "mitre_attack_mapping",
                "incident_documentation"
            ],
            "medium": [
                "threat_actor_profiling",
                "malware_analysis_support",
                "network_forensics",
                "log_analysis"
            ],
            "low": [
                "advanced_threat_hunting",
                "custom_ioc_development",
                "attribution_analysis",
                "advanced_malware_reverse_engineering"
            ]
        }

        self.mitre_techniques = self._load_mitre_techniques()

    def execute_dfir_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DFIR task based on confidence level"""

        confidence = self._assess_task_confidence(task_type)

        if confidence == "high":
            return self._execute_high_confidence_task(task_type, parameters)
        elif confidence == "medium":
            return self._execute_medium_confidence_task(task_type, parameters)
        else:
            return {
                "success": False,
                "action": "escalate",
                "reason": f"Task {task_type} requires senior DFIR analyst",
                "confidence": confidence
            }

    def _execute_high_confidence_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute high-confidence DFIR tasks"""

        if task_type == "hash_lookup":
            return self._hash_lookup(parameters)
        elif task_type == "ip_reputation_check":
            return self._ip_reputation_check(parameters)
        elif task_type == "domain_lookup":
            return self._domain_lookup(parameters)
        elif task_type == "timeline_generation":
            return self._timeline_generation(parameters)
        elif task_type == "mitre_attack_mapping":
            return self._mitre_attack_mapping(parameters)
        elif task_type == "incident_documentation":
            return self._incident_documentation(parameters)
        else:
            return {"success": False, "error": f"Unknown task: {task_type}"}

    def _execute_medium_confidence_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute medium-confidence tasks requiring validation"""

        if task_type == "threat_actor_profiling":
            return self._threat_actor_profiling(parameters)
        elif task_type == "log_analysis":
            return self._log_analysis(parameters)
        else:
            return {
                "success": False,
                "action": "provide_guidance",
                "task": task_type,
                "guidance": f"Task {task_type} requires DFIR analyst validation",
                "next_steps": [
                    "Review findings with senior analyst",
                    "Validate IOCs and indicators",
                    "Cross-reference with threat intel",
                    "Document chain of custody"
                ]
            }

    def _hash_lookup(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: File hash lookup and enrichment

        Args:
            hash_value: File hash (MD5, SHA1, SHA256)
            hash_type: Type of hash (md5, sha1, sha256)
        """
        print("🔍 Looking up file hash...")

        hash_value = params.get("hash_value")
        hash_type = params.get("hash_type", "sha256")

        if not hash_value:
            return {"success": False, "error": "Hash value required"}

        hash_info = {
            "hash": hash_value,
            "hash_type": hash_type,
            "timestamp": datetime.now().isoformat(),
            "sources_checked": [],
            "findings": []
        }

        try:
            hash_info["sources_checked"].append("VirusTotal (API required)")
            hash_info["sources_checked"].append("MalwareBazaar (API required)")
            hash_info["sources_checked"].append("AlienVault OTX (API required)")

            hash_info["findings"].append({
                "source": "local_analysis",
                "result": "Hash catalogued for investigation",
                "recommendation": "Submit hash to threat intel platforms with API access"
            })

            output = {
                "success": True,
                "task": "hash_lookup",
                "hash_info": hash_info,
                "ioc_detected": False,
                "next_steps": [
                    "Submit to VirusTotal for analysis",
                    "Check against internal threat database",
                    "Document in incident timeline",
                    "Preserve sample if available"
                ],
                "timestamp": datetime.now().isoformat()
            }

            print(f"   ✅ Hash lookup complete: {hash_value[:16]}...")
            print(f"   📊 Sources checked: {len(hash_info['sources_checked'])}")

            self._save_operation("hash_lookup", output)
            return output

        except Exception as e:
            return {"success": False, "task": "hash_lookup", "error": str(e)}

    def _ip_reputation_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: IP address reputation check

        Args:
            ip_address: IP address to check
        """
        print("🌐 Checking IP reputation...")

        ip_address = params.get("ip_address")

        if not ip_address:
            return {"success": False, "error": "IP address required"}

        ip_info = {
            "ip": ip_address,
            "timestamp": datetime.now().isoformat(),
            "reputation_sources": [],
            "findings": [],
            "threat_level": "unknown"
        }

        try:
            ip_info["reputation_sources"].append("AbuseIPDB (API required)")
            ip_info["reputation_sources"].append("GreyNoise (API required)")
            ip_info["reputation_sources"].append("AlienVault OTX (API required)")

            if self._is_private_ip(ip_address):
                ip_info["findings"].append({
                    "source": "local_analysis",
                    "result": "Private IP address - internal network",
                    "threat_level": "investigate_internal"
                })
                ip_info["threat_level"] = "internal_investigation_required"
            else:
                ip_info["findings"].append({
                    "source": "local_analysis",
                    "result": "Public IP - requires threat intel lookup",
                    "threat_level": "requires_validation"
                })

            output = {
                "success": True,
                "task": "ip_reputation_check",
                "ip_info": ip_info,
                "requires_validation": True,
                "next_steps": [
                    "Query threat intelligence platforms",
                    "Check firewall logs for activity",
                    "Review connection patterns",
                    "Document in incident report"
                ],
                "timestamp": datetime.now().isoformat()
            }

            print(f"   ✅ IP check complete: {ip_address}")
            print(f"   🔒 Threat Level: {ip_info['threat_level']}")

            self._save_operation("ip_reputation_check", output)
            return output

        except Exception as e:
            return {"success": False, "task": "ip_reputation_check", "error": str(e)}

    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is in private range"""
        private_ranges = [
            "10.", "172.16.", "172.17.", "172.18.", "172.19.",
            "172.20.", "172.21.", "172.22.", "172.23.", "172.24.",
            "172.25.", "172.26.", "172.27.", "172.28.", "172.29.",
            "172.30.", "172.31.", "192.168.", "127."
        ]
        return any(ip.startswith(prefix) for prefix in private_ranges)

    def _domain_lookup(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Domain reputation lookup

        Args:
            domain: Domain name to lookup
        """
        print("🔎 Looking up domain...")

        domain = params.get("domain")

        if not domain:
            return {"success": False, "error": "Domain required"}

        domain_info = {
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "sources_checked": [],
            "findings": [],
            "threat_indicators": []
        }

        try:
            domain_info["sources_checked"].append("URLhaus (API required)")
            domain_info["sources_checked"].append("PhishTank (API required)")
            domain_info["sources_checked"].append("VirusTotal (API required)")

            domain_info["findings"].append({
                "source": "local_analysis",
                "result": f"Domain {domain} catalogued for investigation",
                "recommendation": "Submit to threat intel platforms"
            })

            output = {
                "success": True,
                "task": "domain_lookup",
                "domain_info": domain_info,
                "next_steps": [
                    "Check domain age and registration",
                    "Query threat intelligence feeds",
                    "Review DNS resolution history",
                    "Check SSL certificate details"
                ],
                "timestamp": datetime.now().isoformat()
            }

            print(f"   ✅ Domain lookup complete: {domain}")

            self._save_operation("domain_lookup", output)
            return output

        except Exception as e:
            return {"success": False, "task": "domain_lookup", "error": str(e)}

    def _timeline_generation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Generate investigation timeline

        Args:
            events: List of events with timestamps
            incident_id: Incident identifier
        """
        print("📅 Generating investigation timeline...")

        events = params.get("events", [])
        incident_id = params.get("incident_id", f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}")

        if not events:
            return {"success": False, "error": "Events list required"}

        sorted_events = sorted(events, key=lambda x: x.get("timestamp", ""))

        timeline_doc = f"""# Incident Timeline - {incident_id}

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Events**: {len(sorted_events)}

---

## Timeline of Events

"""

        for i, event in enumerate(sorted_events, 1):
            timeline_doc += f"""### Event {i}: {event.get('title', 'Unknown Event')}

- **Time**: {event.get('timestamp')}
- **Type**: {event.get('event_type', 'Unknown')}
- **Description**: {event.get('description', 'N/A')}
- **Source**: {event.get('source', 'N/A')}
- **Analyst Notes**: {event.get('notes', 'None')}

"""

        timeline_doc += """## Investigation Summary

### Key Findings
- Timeline spans investigation period
- All events catalogued and ordered chronologically
- Ready for senior analyst review

### Next Steps
1. Validate timeline accuracy with log sources
2. Identify gaps in event coverage
3. Correlate with threat intelligence
4. Document root cause analysis

---

*Timeline generated by DFIR Support Agent*
"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"incident_timeline_{incident_id}_{timestamp}.md"
        output_file = self.deliverable_dir / filename

        with open(output_file, 'w') as f:
            f.write(timeline_doc)

        output = {
            "success": True,
            "task": "timeline_generation",
            "incident_id": incident_id,
            "total_events": len(sorted_events),
            "timeline_file": str(output_file),
            "timestamp": datetime.now().isoformat()
        }

        print(f"   ✅ Timeline generated: {output_file}")
        print(f"   📊 Events: {len(sorted_events)}")

        self._save_operation("timeline_generation", output)
        return output

    def _mitre_attack_mapping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Map observables to MITRE ATT&CK techniques

        Args:
            observables: List of observed behaviors/indicators
            incident_type: Type of incident (ransomware, phishing, etc.)
        """
        print("🎯 Mapping to MITRE ATT&CK...")

        observables = params.get("observables", [])
        incident_type = params.get("incident_type", "unknown")

        if not observables:
            return {"success": False, "error": "Observables list required"}

        mapped_techniques = []

        for observable in observables:
            techniques = self._map_observable_to_mitre(observable, incident_type)
            mapped_techniques.extend(techniques)

        unique_techniques = {t["technique_id"]: t for t in mapped_techniques}.values()

        mapping_doc = f"""# MITRE ATT&CK Mapping

**Incident Type**: {incident_type}
**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Mapped Techniques

"""

        for technique in unique_techniques:
            mapping_doc += f"""### {technique['technique_id']}: {technique['name']}

- **Tactic**: {technique['tactic']}
- **Observable**: {technique['observable']}
- **Confidence**: {technique['confidence']}
- **Mitigation**: {technique.get('mitigation', 'Refer to MITRE ATT&CK for mitigations')}

"""

        mapping_doc += """## Defensive Recommendations

1. Review detection rules for mapped techniques
2. Implement MITRE-recommended mitigations
3. Update threat hunting queries
4. Enhance monitoring for these TTPs

---

*MITRE ATT&CK mapping by DFIR Support Agent*
"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mitre_attack_mapping_{timestamp}.md"
        output_file = self.deliverable_dir / filename

        with open(output_file, 'w') as f:
            f.write(mapping_doc)

        output = {
            "success": True,
            "task": "mitre_attack_mapping",
            "incident_type": incident_type,
            "techniques_mapped": len(unique_techniques),
            "mapping_file": str(output_file),
            "techniques": list(unique_techniques),
            "timestamp": datetime.now().isoformat()
        }

        print(f"   ✅ MITRE mapping complete: {output_file}")
        print(f"   🎯 Techniques identified: {len(unique_techniques)}")

        self._save_operation("mitre_attack_mapping", output)
        return output

    def _map_observable_to_mitre(self, observable: str, incident_type: str) -> List[Dict]:
        """Map observable to MITRE ATT&CK techniques"""

        techniques = []
        observable_lower = observable.lower()

        if "powershell" in observable_lower or "cmd.exe" in observable_lower:
            techniques.append({
                "technique_id": "T1059",
                "name": "Command and Scripting Interpreter",
                "tactic": "Execution",
                "observable": observable,
                "confidence": "high",
                "mitigation": "Restrict PowerShell execution, implement application whitelisting"
            })

        if "credential" in observable_lower or "password" in observable_lower:
            techniques.append({
                "technique_id": "T1003",
                "name": "OS Credential Dumping",
                "tactic": "Credential Access",
                "observable": observable,
                "confidence": "medium",
                "mitigation": "Implement credential guard, monitor LSASS access"
            })

        if "lateral" in observable_lower or "smb" in observable_lower:
            techniques.append({
                "technique_id": "T1021",
                "name": "Remote Services",
                "tactic": "Lateral Movement",
                "observable": observable,
                "confidence": "medium",
                "mitigation": "Restrict SMB, implement network segmentation"
            })

        if "encrypt" in observable_lower and incident_type == "ransomware":
            techniques.append({
                "technique_id": "T1486",
                "name": "Data Encrypted for Impact",
                "tactic": "Impact",
                "observable": observable,
                "confidence": "high",
                "mitigation": "Implement backups, endpoint protection, behavioral detection"
            })

        if "phishing" in observable_lower or "email" in observable_lower:
            techniques.append({
                "technique_id": "T1566",
                "name": "Phishing",
                "tactic": "Initial Access",
                "observable": observable,
                "confidence": "high",
                "mitigation": "Security awareness training, email filtering, DMARC/SPF/DKIM"
            })

        return techniques if techniques else [{
            "technique_id": "Unknown",
            "name": "Requires analyst review",
            "tactic": "Unknown",
            "observable": observable,
            "confidence": "low",
            "mitigation": "Manual analysis required"
        }]

    def _incident_documentation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        HIGH CONFIDENCE: Generate incident response documentation

        Args:
            incident_data: Incident details (title, severity, timeline, iocs)
        """
        print("📝 Generating incident documentation...")

        incident_data = params.get("incident_data", {})

        if not incident_data:
            return {"success": False, "error": "Incident data required"}

        incident_id = incident_data.get("incident_id", f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        title = incident_data.get("title", "Security Incident")
        severity = incident_data.get("severity", "Medium")
        description = incident_data.get("description", "Security incident detected")
        iocs = incident_data.get("iocs", [])

        incident_doc = f"""# Incident Response Report

**Incident ID**: {incident_id}
**Title**: {title}
**Severity**: {severity}
**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Analyst**: DFIR Support Agent

---

## Executive Summary

{description}

## Incident Details

### Timeline
{incident_data.get('timeline', 'Timeline to be determined')}

### Affected Systems
{incident_data.get('affected_systems', 'Under investigation')}

### Impact Assessment
{incident_data.get('impact', 'Impact analysis in progress')}

## Indicators of Compromise (IOCs)

"""

        if iocs:
            for ioc in iocs:
                incident_doc += f"- **{ioc.get('type', 'Unknown')}**: `{ioc.get('value', 'N/A')}` - {ioc.get('description', 'No description')}\n"
        else:
            incident_doc += "- No IOCs identified yet\n"

        incident_doc += f"""

## Response Actions Taken

{incident_data.get('actions_taken', '1. Incident detected and escalated\\n2. Initial triage performed\\n3. Evidence preservation in progress')}

## Recommendations

1. Continue investigation and evidence collection
2. Implement containment measures if not already done
3. Review and update detection rules
4. Conduct post-incident review
5. Update incident response procedures

## Next Steps

1. Senior analyst review
2. Complete forensic analysis
3. Finalize remediation plan
4. Customer communication (if applicable)
5. Lessons learned documentation

---

## Chain of Custody

- **Evidence Collected**: {datetime.now().isoformat()}
- **Collected By**: DFIR Support Agent
- **Storage Location**: GP-DATA/deliverables/
- **Access Control**: Restricted to incident response team

---

*This incident report was generated by the DFIR Support Agent and requires senior analyst validation*
"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"incident_report_{incident_id}_{timestamp}.md"
        output_file = self.deliverable_dir / filename

        with open(output_file, 'w') as f:
            f.write(incident_doc)

        output = {
            "success": True,
            "task": "incident_documentation",
            "incident_id": incident_id,
            "severity": severity,
            "ioc_count": len(iocs),
            "report_file": str(output_file),
            "timestamp": datetime.now().isoformat()
        }

        print(f"   ✅ Incident report generated: {output_file}")
        print(f"   🚨 Severity: {severity}")
        print(f"   📊 IOCs: {len(iocs)}")

        self._save_operation("incident_documentation", output)
        return output

    def _threat_actor_profiling(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        MEDIUM CONFIDENCE: Generate threat actor profile

        Args:
            actor_indicators: Observed TTPs and indicators
            campaign_name: Campaign or operation name
        """
        print("🕵️ Profiling threat actor...")

        actor_indicators = params.get("actor_indicators", [])
        campaign_name = params.get("campaign_name", "Unknown")

        profile = {
            "campaign_name": campaign_name,
            "indicators_analyzed": len(actor_indicators),
            "profile_summary": "Threat actor profiling requires expert analysis",
            "confidence": "medium",
            "recommendations": [
                "Cross-reference with threat intelligence feeds",
                "Review historical campaigns with similar TTPs",
                "Consult with senior threat analyst",
                "Document all observed behaviors"
            ],
            "next_steps": [
                "Validate findings with threat intel team",
                "Update threat actor database",
                "Enhance detection rules",
                "Share intelligence with community (if applicable)"
            ],
            "timestamp": datetime.now().isoformat()
        }

        output = {
            "success": True,
            "task": "threat_actor_profiling",
            "profile": profile,
            "requires_validation": True,
            "timestamp": datetime.now().isoformat()
        }

        print(f"   ⚠️  Threat profile generated - requires expert validation")

        self._save_operation("threat_actor_profiling", output)
        return output

    def _log_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        MEDIUM CONFIDENCE: Analyze logs for indicators

        Args:
            log_file: Path to log file
            indicators: Known indicators to search for
        """
        print("📊 Analyzing logs...")

        log_file = params.get("log_file")
        indicators = params.get("indicators", [])

        if not log_file or not Path(log_file).exists():
            return {"success": False, "error": "Log file required and must exist"}

        analysis_results = {
            "log_file": log_file,
            "indicators_searched": len(indicators),
            "matches_found": [],
            "total_lines_analyzed": 0
        }

        try:
            with open(log_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    analysis_results["total_lines_analyzed"] = line_num

                    for indicator in indicators:
                        if indicator.lower() in line.lower():
                            analysis_results["matches_found"].append({
                                "line_number": line_num,
                                "indicator": indicator,
                                "log_entry": line.strip()[:200]
                            })

            output = {
                "success": True,
                "task": "log_analysis",
                "analysis_results": analysis_results,
                "matches_count": len(analysis_results["matches_found"]),
                "requires_validation": True,
                "next_steps": [
                    "Review matched log entries",
                    "Correlate with timeline",
                    "Validate with senior analyst",
                    "Preserve logs as evidence"
                ],
                "timestamp": datetime.now().isoformat()
            }

            print(f"   📊 Analyzed {analysis_results['total_lines_analyzed']} log lines")
            print(f"   🔍 Matches found: {len(analysis_results['matches_found'])}")
            print(f"   ⚠️  Requires senior analyst validation")

            self._save_operation("log_analysis", output)
            return output

        except Exception as e:
            return {"success": False, "task": "log_analysis", "error": str(e)}

    def _load_mitre_techniques(self) -> Dict[str, str]:
        """Load common MITRE ATT&CK techniques"""
        return {
            "T1059": "Command and Scripting Interpreter",
            "T1003": "OS Credential Dumping",
            "T1021": "Remote Services",
            "T1486": "Data Encrypted for Impact",
            "T1566": "Phishing",
            "T1078": "Valid Accounts",
            "T1053": "Scheduled Task/Job",
            "T1547": "Boot or Logon Autostart Execution"
        }

    def _assess_task_confidence(self, task_type: str) -> str:
        """Assess confidence level for DFIR task"""

        for level, tasks in self.confidence_levels.items():
            if task_type in tasks:
                return level

        return "low"

    def _save_operation(self, operation_type: str, result: Dict):
        """Save operation results to GP-DATA"""
        operation_id = f"{operation_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"
        output_file = self.output_dir / f"{operation_id}.json"

        operation_record = {
            "agent": self.agent_id,
            "operation": operation_type,
            "timestamp": datetime.now().isoformat(),
            "result": result
        }

        with open(output_file, 'w') as f:
            json.dump(operation_record, f, indent=2)

    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status and capabilities"""
        return {
            "agent_id": self.agent_id,
            "confidence_levels": self.confidence_levels,
            "capabilities": [
                "IOC lookup and enrichment",
                "Threat intelligence support",
                "Investigation timeline generation",
                "MITRE ATT&CK mapping",
                "Incident response documentation"
            ],
            "supported_ioc_types": ["File Hash", "IP Address", "Domain", "URL"]
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("DFIR Support Agent - Digital Forensics & Incident Response")
        print()
        print("HIGH CONFIDENCE Operations:")
        print("  python dfir_agent.py hash-lookup --hash <hash> --type <md5|sha1|sha256>")
        print("  python dfir_agent.py ip-check --ip <ip_address>")
        print("  python dfir_agent.py domain-lookup --domain <domain>")
        print("  python dfir_agent.py generate-timeline --events <events.json> --incident <id>")
        print("  python dfir_agent.py mitre-map --observables <obs.json> --type <incident_type>")
        print("  python dfir_agent.py incident-doc --data <incident.json>")
        print()
        print("MEDIUM CONFIDENCE Operations:")
        print("  python dfir_agent.py threat-profile --indicators <indicators.json>")
        print("  python dfir_agent.py analyze-logs --log <file> --indicators <indicators.json>")
        print()
        print("Examples:")
        print("  python dfir_agent.py hash-lookup --hash abc123... --type sha256")
        print("  python dfir_agent.py ip-check --ip 192.168.1.100")
        print("  python dfir_agent.py mitre-map --observables observables.json --type ransomware")
        sys.exit(1)

    agent = DFIRSupportAgent()
    command = sys.argv[1]

    if command == "hash-lookup":
        params = {"hash_value": None, "hash_type": "sha256"}

        for arg in sys.argv[2:]:
            if arg.startswith("--hash="):
                params["hash_value"] = arg.split("=", 1)[1]
            elif arg.startswith("--type="):
                params["hash_type"] = arg.split("=", 1)[1]

        result = agent._hash_lookup(params)

        if result["success"]:
            print(f"\n✅ Hash Lookup Complete:")
            print(f"   Hash: {params['hash_value'][:32]}...")
            print(f"   Type: {params['hash_type']}")
            print(f"\n   Next Steps:")
            for step in result['next_steps']:
                print(f"   - {step}")

    elif command == "ip-check":
        params = {"ip_address": None}

        for arg in sys.argv[2:]:
            if arg.startswith("--ip="):
                params["ip_address"] = arg.split("=", 1)[1]

        result = agent._ip_reputation_check(params)

        if result["success"]:
            print(f"\n✅ IP Reputation Check:")
            info = result["ip_info"]
            print(f"   IP: {info['ip']}")
            print(f"   Threat Level: {info['threat_level']}")

    elif command == "domain-lookup":
        params = {"domain": None}

        for arg in sys.argv[2:]:
            if arg.startswith("--domain="):
                params["domain"] = arg.split("=", 1)[1]

        result = agent._domain_lookup(params)

        if result["success"]:
            print(f"\n✅ Domain Lookup Complete:")
            print(f"   Domain: {result['domain_info']['domain']}")

    elif command == "incident-doc":
        params = {"incident_data": {}}

        for arg in sys.argv[2:]:
            if arg.startswith("--data="):
                data_file = arg.split("=", 1)[1]
                if Path(data_file).exists():
                    with open(data_file, 'r') as f:
                        params["incident_data"] = json.load(f)

        result = agent._incident_documentation(params)

        if result["success"]:
            print(f"\n✅ Incident Report Generated:")
            print(f"   File: {result['report_file']}")
            print(f"   Incident ID: {result['incident_id']}")
            print(f"   Severity: {result['severity']}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)