#!/usr/bin/env python3
"""
Policy Impact Analyzer
Automated compliance risk assessment and impact analysis for policy changes.

This module analyzes policy diffs and automatically flags compliance impacts,
operational consequences, and generates actionable recommendations.
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class RiskLevel(Enum):
    """Risk severity levels for policy changes."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    PCI_DSS = "PCI-DSS"
    SOC2 = "SOC2"
    ISO27001 = "ISO27001"


class PolicyImpactAnalyzer:
    """
    Analyzes policy changes and generates compliance impact reports.
    
    Features:
    - Compliance risk detection (GDPR, HIPAA, PCI-DSS, SOC2, ISO27001)
    - Operational impact analysis (performance, volume, privacy)
    - Automated risk scoring (critical/high/medium/low)
    - Actionable recommendations
    - Human and machine-readable outputs
    """
    
    def __init__(self):
        """Initialize the impact analyzer."""
        self.compliance_rules = self._init_compliance_rules()
        self.operational_rules = self._init_operational_rules()
    
    def _init_compliance_rules(self) -> Dict[str, Any]:
        """Initialize compliance framework rules."""
        return {
            ComplianceFramework.GDPR.value: {
                "pii_fields": ["email", "user_id", "ip_address", "name", "address", "phone"],
                "retention_critical": True,
                "redaction_required": True,
                "consent_tracking": True,
                "articles": ["Article 5(1)(a)", "Article 5(1)(c)", "Article 5(1)(e)", "Article 5(2)"]
            },
            ComplianceFramework.HIPAA.value: {
                "phi_fields": ["patient_id", "medical_record", "diagnosis", "health_data", "prescription"],
                "encryption_required": True,
                "access_logging": True,
                "retention_years": 6,
                "sections": ["§164.308(a)(1)(ii)(D)", "§164.312(a)(2)(iv)", "§164.530(j)"]
            },
            ComplianceFramework.PCI_DSS.value: {
                "cardholder_data": ["card_number", "cvv", "expiry_date", "cardholder_name"],
                "encryption_mandatory": True,
                "retention_days": 90,
                "audit_trails": True,
                "requirements": ["Requirement 3", "Requirement 10"]
            },
            ComplianceFramework.SOC2.value: {
                "security_logging": True,
                "access_controls": True,
                "change_management": True,
                "criteria": ["CC6.1", "CC6.6", "CC6.7", "CC7.2"]
            },
            ComplianceFramework.ISO27001.value: {
                "information_security": True,
                "risk_assessment": True,
                "controls": ["A.12.4.1", "A.12.4.2", "A.12.4.3", "A.18.1.5"]
            }
        }
    
    def _init_operational_rules(self) -> Dict[str, Any]:
        """Initialize operational impact rules."""
        return {
            "performance": {
                "pattern_complexity": {"threshold": 10, "impact": "high"},
                "field_count": {"threshold": 50, "impact": "medium"},
                "enforcement_level": {"strict": "high", "moderate": "medium", "lenient": "low"}
            },
            "logging_volume": {
                "redaction_increase": {"threshold": 0.2, "impact": "medium"},
                "blocking_increase": {"threshold": 0.1, "impact": "high"}
            },
            "privacy": {
                "pii_exposure": "critical",
                "phi_exposure": "critical",
                "redaction_removal": "high",
                "encryption_removal": "high"
            }
        }
    
    def analyze(self, policy_diff: Dict[str, Any], old_policy: Optional[Dict] = None, 
                new_policy: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze policy changes and generate impact report.
        
        Args:
            policy_diff: Diff output from PolicyDiffer
            old_policy: Previous policy configuration (optional)
            new_policy: New policy configuration (optional)
        
        Returns:
            Comprehensive impact analysis with risks and recommendations
        """
        impacts = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "summary": {
                "total_changes": len(policy_diff.get("changes", [])),
                "risk_level": RiskLevel.INFO.value,
                "compliance_frameworks_affected": [],
                "operational_impacts": []
            },
            "compliance_impacts": [],
            "operational_impacts": [],
            "recommendations": [],
            "risk_score": 0
        }
        
        changes = policy_diff.get("changes", [])
        
        # Analyze compliance impacts
        compliance_impacts = self._analyze_compliance_impacts(changes, old_policy, new_policy)
        impacts["compliance_impacts"] = compliance_impacts
        
        # Analyze operational impacts
        operational_impacts = self._analyze_operational_impacts(changes, old_policy, new_policy)
        impacts["operational_impacts"] = operational_impacts
        
        # Calculate overall risk score and level
        risk_score, risk_level = self._calculate_risk(compliance_impacts, operational_impacts)
        impacts["risk_score"] = risk_score
        impacts["summary"]["risk_level"] = risk_level.value
        
        # Extract affected frameworks
        frameworks = set()
        for impact in compliance_impacts:
            frameworks.add(impact["framework"])
        impacts["summary"]["compliance_frameworks_affected"] = sorted(list(frameworks))
        
        # Extract operational impact types
        op_types = set()
        for impact in operational_impacts:
            op_types.add(impact["category"])
        impacts["summary"]["operational_impacts"] = sorted(list(op_types))
        
        # Generate recommendations
        impacts["recommendations"] = self._generate_recommendations(
            compliance_impacts, operational_impacts, risk_level
        )
        
        return impacts
    
    def _analyze_compliance_impacts(self, changes: List[Dict], old_policy: Optional[Dict],
                                   new_policy: Optional[Dict]) -> List[Dict]:
        """Analyze compliance framework impacts."""
        impacts = []
        
        for change in changes:
            field_path = change.get("field", "")
            change_type = change.get("type", "")
            old_value = change.get("old_value")
            new_value = change.get("new_value")
            
            # Check GDPR impacts
            if any(pii in field_path.lower() for pii in ["pii", "personal", "email", "user_id", "ip_address"]):
                if "required_tags" in field_path and change_type == "removed":
                    impacts.append({
                        "framework": ComplianceFramework.GDPR.value,
                        "risk_level": RiskLevel.CRITICAL.value,
                        "field": field_path,
                        "issue": "PII field no longer requires privacy tags",
                        "article": "Article 5(1)(f) - Data must be processed securely",
                        "description": f"Removing privacy tag requirements for {field_path} may lead to unredacted PII in logs"
                    })
                elif "redaction_required" in field_path and not new_value:
                    impacts.append({
                        "framework": ComplianceFramework.GDPR.value,
                        "risk_level": RiskLevel.HIGH.value,
                        "field": field_path,
                        "issue": "PII redaction disabled",
                        "article": "Article 25 - Data protection by design",
                        "description": "Disabling PII redaction violates data minimization principles"
                    })
            
            # Check HIPAA impacts
            if any(phi in field_path.lower() for phi in ["phi", "patient", "medical", "health", "diagnosis"]):
                if "encryption" in field_path and not new_value:
                    impacts.append({
                        "framework": ComplianceFramework.HIPAA.value,
                        "risk_level": RiskLevel.CRITICAL.value,
                        "field": field_path,
                        "issue": "PHI encryption disabled",
                        "section": "§164.312(a)(2)(iv) - Encryption required for ePHI",
                        "description": "Removing PHI encryption violates HIPAA Security Rule"
                    })
            
            # Check PCI-DSS impacts
            if any(card in field_path.lower() for card in ["card", "cvv", "cardholder", "payment"]):
                if "retention" in field_path and old_value and new_value:
                    old_days = old_value if isinstance(old_value, (int, float)) else 0
                    new_days = new_value if isinstance(new_value, (int, float)) else 0
                    if new_days > old_days:
                        impacts.append({
                            "framework": ComplianceFramework.PCI_DSS.value,
                            "risk_level": RiskLevel.HIGH.value,
                            "field": field_path,
                            "issue": "Cardholder data retention increased",
                            "requirement": "Requirement 3.1 - Minimize cardholder data retention",
                            "description": f"Increased retention from {old_days} to {new_days} days may violate PCI-DSS"
                        })
            
            # Check SOC2 impacts
            if "enforcement_level" in field_path:
                if new_value == "lenient" and old_value in ["strict", "moderate"]:
                    impacts.append({
                        "framework": ComplianceFramework.SOC2.value,
                        "risk_level": RiskLevel.MEDIUM.value,
                        "field": field_path,
                        "issue": "Enforcement level reduced",
                        "criteria": "CC6.1 - Logical and physical access controls",
                        "description": "Weakening enforcement may compromise security monitoring"
                    })
            
            # Check ISO27001 impacts
            if "audit" in field_path.lower() or "logging" in field_path.lower():
                if change_type == "removed" or (change_type == "modified" and not new_value):
                    impacts.append({
                        "framework": ComplianceFramework.ISO27001.value,
                        "risk_level": RiskLevel.HIGH.value,
                        "field": field_path,
                        "issue": "Audit logging reduced",
                        "control": "A.12.4.1 - Event logging",
                        "description": "Reducing audit logging may violate ISO27001 control requirements"
                    })
        
        return impacts
    
    def _analyze_operational_impacts(self, changes: List[Dict], old_policy: Optional[Dict],
                                    new_policy: Optional[Dict]) -> List[Dict]:
        """Analyze operational impacts."""
        impacts = []
        
        for change in changes:
            field_path = change.get("field", "")
            change_type = change.get("type", "")
            old_value = change.get("old_value")
            new_value = change.get("new_value")
            
            # Performance impacts
            if "pattern_detection" in field_path:
                if change_type == "added" or (isinstance(new_value, list) and isinstance(old_value, list) 
                                             and len(new_value) > len(old_value)):
                    pattern_count = len(new_value) if isinstance(new_value, list) else 1
                    if pattern_count > self.operational_rules["performance"]["pattern_complexity"]["threshold"]:
                        impacts.append({
                            "category": "performance",
                            "risk_level": RiskLevel.HIGH.value,
                            "field": field_path,
                            "issue": "High pattern complexity",
                            "description": f"{pattern_count} regex patterns may impact log processing performance",
                            "impact": "Increased CPU usage during log validation"
                        })
            
            # Logging volume impacts
            if "enforcement_level" in field_path:
                if new_value == "strict" and old_value in ["lenient", "moderate"]:
                    impacts.append({
                        "category": "logging_volume",
                        "risk_level": RiskLevel.MEDIUM.value,
                        "field": field_path,
                        "issue": "Stricter enforcement may reduce log volume",
                        "description": "More logs may be rejected, potentially losing diagnostic information",
                        "impact": "5-20% reduction in accepted logs estimated"
                    })
            
            # Privacy impacts
            if "suspect_fields" in field_path and "pii" in field_path.lower():
                if change_type == "removed" or (isinstance(new_value, list) and isinstance(old_value, list)
                                               and len(new_value) < len(old_value)):
                    impacts.append({
                        "category": "privacy",
                        "risk_level": RiskLevel.CRITICAL.value,
                        "field": field_path,
                        "issue": "PII detection scope reduced",
                        "description": "Fewer fields monitored for PII may allow sensitive data in logs",
                        "impact": "Increased risk of privacy violations"
                    })
        
        return impacts
    
    def _calculate_risk(self, compliance_impacts: List[Dict], 
                       operational_impacts: List[Dict]) -> tuple:
        """Calculate overall risk score and level."""
        risk_scores = {
            RiskLevel.CRITICAL.value: 100,
            RiskLevel.HIGH.value: 50,
            RiskLevel.MEDIUM.value: 20,
            RiskLevel.LOW.value: 5,
            RiskLevel.INFO.value: 0
        }
        
        total_score = 0
        
        # Score compliance impacts (weighted 2x)
        for impact in compliance_impacts:
            score = risk_scores.get(impact.get("risk_level", RiskLevel.INFO.value), 0)
            total_score += score * 2
        
        # Score operational impacts
        for impact in operational_impacts:
            score = risk_scores.get(impact.get("risk_level", RiskLevel.INFO.value), 0)
            total_score += score
        
        # Determine risk level
        if total_score >= 200:
            risk_level = RiskLevel.CRITICAL
        elif total_score >= 100:
            risk_level = RiskLevel.HIGH
        elif total_score >= 40:
            risk_level = RiskLevel.MEDIUM
        elif total_score > 0:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.INFO
        
        return total_score, risk_level
    
    def _generate_recommendations(self, compliance_impacts: List[Dict],
                                 operational_impacts: List[Dict],
                                 risk_level: RiskLevel) -> List[Dict]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Critical risk recommendations
        if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            recommendations.append({
                "priority": "immediate",
                "action": "Review all CRITICAL and HIGH risk changes before deployment",
                "rationale": "Policy changes may violate compliance requirements"
            })
            
            recommendations.append({
                "priority": "immediate",
                "action": "Obtain legal/compliance team approval",
                "rationale": "Changes affect regulated data handling"
            })
        
        # Framework-specific recommendations
        frameworks_affected = set(impact["framework"] for impact in compliance_impacts)
        
        if ComplianceFramework.GDPR.value in frameworks_affected:
            recommendations.append({
                "priority": "high",
                "action": "Conduct GDPR Data Protection Impact Assessment (DPIA)",
                "rationale": "Article 35 requires DPIA for high-risk processing changes"
            })
        
        if ComplianceFramework.HIPAA.value in frameworks_affected:
            recommendations.append({
                "priority": "high",
                "action": "Update HIPAA risk analysis documentation",
                "rationale": "§164.308(a)(1)(ii)(A) requires ongoing risk analysis"
            })
        
        if ComplianceFramework.PCI_DSS.value in frameworks_affected:
            recommendations.append({
                "priority": "high",
                "action": "Notify Qualified Security Assessor (QSA)",
                "rationale": "Material changes require QSA review before next assessment"
            })
        
        # Operational recommendations
        has_performance_impact = any(i["category"] == "performance" for i in operational_impacts)
        if has_performance_impact:
            recommendations.append({
                "priority": "medium",
                "action": "Conduct performance testing with new policy",
                "rationale": "Pattern complexity changes may impact throughput"
            })
        
        has_volume_impact = any(i["category"] == "logging_volume" for i in operational_impacts)
        if has_volume_impact:
            recommendations.append({
                "priority": "medium",
                "action": "Review monitoring dashboards and alerts",
                "rationale": "Log volume changes may trigger false positives or miss critical events"
            })
        
        # General best practices
        recommendations.append({
            "priority": "low",
            "action": "Document policy change in change management system",
            "rationale": "Maintains audit trail for compliance reviews"
        })
        
        recommendations.append({
            "priority": "low",
            "action": "Schedule retrospective review in 30 days",
            "rationale": "Verify policy changes achieved intended outcomes"
        })
        
        return recommendations
    
    def format_human_readable(self, analysis: Dict[str, Any]) -> str:
        """Format analysis as human-readable text."""
        output = []
        output.append("=" * 80)
        output.append("POLICY IMPACT ANALYSIS REPORT")
        output.append("=" * 80)
        output.append(f"Generated: {analysis['timestamp']}")
        output.append(f"Risk Level: {analysis['summary']['risk_level'].upper()}")
        output.append(f"Risk Score: {analysis['risk_score']}")
        output.append(f"Total Changes: {analysis['summary']['total_changes']}")
        output.append("")
        
        # Summary
        output.append("SUMMARY")
        output.append("-" * 80)
        if analysis['summary']['compliance_frameworks_affected']:
            output.append(f"Compliance Frameworks Affected: {', '.join(analysis['summary']['compliance_frameworks_affected'])}")
        if analysis['summary']['operational_impacts']:
            output.append(f"Operational Impact Categories: {', '.join(analysis['summary']['operational_impacts'])}")
        output.append("")
        
        # Compliance Impacts
        if analysis['compliance_impacts']:
            output.append("COMPLIANCE IMPACTS")
            output.append("-" * 80)
            for i, impact in enumerate(analysis['compliance_impacts'], 1):
                output.append(f"\n{i}. [{impact['risk_level'].upper()}] {impact['framework']}")
                output.append(f"   Field: {impact['field']}")
                output.append(f"   Issue: {impact['issue']}")
                output.append(f"   Reference: {impact.get('article') or impact.get('section') or impact.get('requirement') or impact.get('criteria') or impact.get('control')}")
                output.append(f"   Description: {impact['description']}")
            output.append("")
        
        # Operational Impacts
        if analysis['operational_impacts']:
            output.append("OPERATIONAL IMPACTS")
            output.append("-" * 80)
            for i, impact in enumerate(analysis['operational_impacts'], 1):
                output.append(f"\n{i}. [{impact['risk_level'].upper()}] {impact['category'].title()}")
                output.append(f"   Field: {impact['field']}")
                output.append(f"   Issue: {impact['issue']}")
                output.append(f"   Description: {impact['description']}")
                output.append(f"   Impact: {impact['impact']}")
            output.append("")
        
        # Recommendations
        if analysis['recommendations']:
            output.append("RECOMMENDATIONS")
            output.append("-" * 80)
            priorities = {"immediate": [], "high": [], "medium": [], "low": []}
            for rec in analysis['recommendations']:
                priorities[rec['priority']].append(rec)
            
            for priority in ["immediate", "high", "medium", "low"]:
                if priorities[priority]:
                    output.append(f"\n{priority.upper()} PRIORITY:")
                    for i, rec in enumerate(priorities[priority], 1):
                        output.append(f"  {i}. {rec['action']}")
                        output.append(f"     Rationale: {rec['rationale']}")
            output.append("")
        
        output.append("=" * 80)
        output.append("END OF REPORT")
        output.append("=" * 80)
        
        return "\n".join(output)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python policy_impact_analyzer.py <diff_file.json> [--output json|text]")
        print("\nAnalyzes policy changes and generates compliance impact report.")
        print("\nOptions:")
        print("  --output json|text    Output format (default: text)")
        sys.exit(1)
    
    diff_file = sys.argv[1]
    output_format = "text"
    
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]
    
    try:
        with open(diff_file, 'r') as f:
            policy_diff = json.load(f)
        
        analyzer = PolicyImpactAnalyzer()
        analysis = analyzer.analyze(policy_diff)
        
        if output_format == "json":
            print(json.dumps(analysis, indent=2))
        else:
            print(analyzer.format_human_readable(analysis))
    
    except FileNotFoundError:
        print(f"Error: File not found: {diff_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {diff_file}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
