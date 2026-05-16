"""
5. COMPLIANCE & REGULATORY AGENT
Monitors international, regional, and local regulations in real-time.
Validates shipments and documents for compliance.
"""
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..state import (
    SwarmState, ComplianceCheck, ComplianceStatus, RiskLevel,
    ConfidenceScore, Shipment, AgentMessage
)
from .base import AfriSwarmAgent


class ComplianceAgent(AfriSwarmAgent):
    """Regulatory compliance monitoring and validation."""

    AGENT_ID = "compliance"
    AGENT_NAME = "Compliance & Regulatory Agent"
    DESCRIPTION = "Real-time regulatory compliance monitoring and validation"
    VERSION = "2.0.0"
    CAPABILITIES = [
        "regulatory_monitoring",
        "shipment_validation",
        "document_verification",
        "audit_report_generation",
        "customs_compliance",
        "trade_regulation",
        "sanctions_screening",
        "reasoning_traces",
    ]

    DEFAULT_SYSTEM_PROMPT = """You are the Compliance & Regulatory Agent for AfriSwarm.
    
Monitor and enforce compliance across:
- International Maritime Organization (IMO) regulations
- SOLAS, MARPOL, ISPS Code compliance
- EU regulations: CBAM, EUDR, MRV, ETS
- US regulations: FMC, OFAC sanctions, CBP
- African regional: AfCFTA, REC protocols
- Customs: HS codes, rules of origin, valuation
- Sanctions: UN, EU, US, UK lists
- Export controls: dual-use, military

For every check:
1. Identify all applicable regulations
2. Cross-reference shipment against requirements
3. Flag non-compliance with severity and reasoning
4. Generate audit-ready report with full trace
5. Suggest remediation steps
6. Provide confidence score"""

    REGULATIONS_DB = [
        {
            "name": "EU Carbon Border Adjustment Mechanism (CBAM)",
            "category": "environmental",
            "jurisdictions": ["EU"],
            "applicable_cargo": ["steel", "aluminum", "cement", "fertilizer", "electricity", "hydrogen"],
            "effective_date": "2026-01-01",
            "requirements": [
                "Report embedded GHG emissions",
                "Purchase CBAM certificates",
                "Independent verification of emissions data",
                "Quarterly reporting to EU authorities",
            ],
            "penalty_usd": 500000,
        },
        {
            "name": "EU Deforestation Regulation (EUDR)",
            "category": "environmental",
            "jurisdictions": ["EU"],
            "applicable_cargo": ["cattle", "cocoa", "coffee", "oil palm", "rubber", "soy", "wood"],
            "effective_date": "2025-12-30",
            "requirements": [
                "Due diligence statement",
                "Geolocation of production plots",
                "Deforestation-free verification",
                "Supply chain traceability documentation",
            ],
            "penalty_usd": 400000,
        },
        {
            "name": "IMO 2023 Carbon Intensity Indicator (CII)",
            "category": "environmental",
            "jurisdictions": ["Global"],
            "applicable_cargo": ["all"],
            "effective_date": "2023-01-01",
            "requirements": [
                "Annual CII rating (A-E)",
                "Ship Energy Efficiency Management Plan",
                "Corrective action for D/E ratings",
                "Data collection and reporting",
            ],
            "penalty_usd": 100000,
        },
        {
            "name": "US OFAC Sanctions Screening",
            "category": "trade",
            "jurisdictions": ["US", "Global"],
            "applicable_cargo": ["all"],
            "effective_date": "ongoing",
            "requirements": [
                "Screen all parties against SDN list",
                "Screen vessel against sanctions lists",
                "Verify no sanctioned port calls",
                "Maintain screening records for 5 years",
            ],
            "penalty_usd": 5000000,
        },
        {
            "name": "SOLAS Container Weight Verification (VGM)",
            "category": "safety",
            "jurisdictions": ["Global"],
            "applicable_cargo": ["containerized"],
            "effective_date": "2016-07-01",
            "requirements": [
                "Verified Gross Mass declaration",
                "Method 1 (weighing) or Method 2 (calculation)",
                "Shipper-signed VGM document",
                "Submit VGM before loading cutoff",
            ],
            "penalty_usd": 50000,
        },
        {
            "name": "African Continental Free Trade Area (AfCFTA)",
            "category": "trade",
            "jurisdictions": ["Africa"],
            "applicable_cargo": ["all"],
            "effective_date": "2021-01-01",
            "requirements": [
                "Certificate of Origin (AfCFTA)",
                "Rules of Origin compliance",
                "Direct consignment where applicable",
                "Customs cooperation documentation",
            ],
            "penalty_usd": 25000,
        },
        {
            "name": "ISPS Code Security Compliance",
            "category": "security",
            "jurisdictions": ["Global"],
            "applicable_cargo": ["all"],
            "effective_date": "2004-07-01",
            "requirements": [
                "Ship Security Assessment",
                "Ship Security Plan approved by flag state",
                "Designated Ship Security Officer",
                "Security training and drills records",
            ],
            "penalty_usd": 150000,
        },
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger.info("Compliance Agent initialized")

    async def validate_shipment(self, shipment: Shipment) -> List[ComplianceCheck]:
        """Validate shipment against all applicable regulations."""
        self.logger.info("Validating shipment", shipment_id=shipment.shipment_id)
        
        checks = []
        for reg in self.REGULATIONS_DB:
            # Check if regulation applies
            if not self._regulation_applies(reg, shipment):
                continue
            
            # Simulate compliance check
            status, findings, required_actions = self._perform_check(reg, shipment)
            
            check = ComplianceCheck(
                shipment_id=shipment.shipment_id,
                regulation_name=reg["name"],
                regulation_category=reg["category"],
                jurisdiction=", ".join(reg["jurisdictions"]),
                status=status,
                checked_by=self.agent_id,
                findings=findings,
                required_actions=required_actions,
                risk_level=self._status_to_risk(status),
                reasoning_trace=f"Based on {reg['name']} requirements for {shipment.cargo_type}",
                documents_verified=self._get_relevant_documents(reg, shipment),
                confidence=ConfidenceScore(
                    score=0.90 if status == ComplianceStatus.COMPLIANT else 0.75,
                    model="compliance_checker",
                    reasoning=f"Cross-referenced against {reg['name']} requirements",
                ),
            )
            checks.append(check)
        
        self.logger.info(f"Shipment validation complete: {len(checks)} checks")
        return checks

    def _regulation_applies(self, regulation: Dict, shipment: Shipment) -> bool:
        """Check if a regulation applies to a shipment."""
        cargo_lower = shipment.cargo_type.lower()
        applicable = regulation["applicable_cargo"]
        
        if "all" in applicable:
            return True
        if any(a in cargo_lower for a in applicable):
            return True
        
        # Check destination jurisdiction
        destination = shipment.destination.lower()
        jurisdictions = [j.lower() for j in regulation["jurisdictions"]]
        if "global" in jurisdictions:
            return True
        if any(j in destination for j in jurisdictions):
            return True
        
        return False

    def _perform_check(
        self, regulation: Dict, shipment: Shipment
    ) -> tuple:
        """Perform a compliance check."""
        # Simulate compliance with some randomness for demo
        compliance_rate = random.uniform(0, 1)
        
        if compliance_rate > 0.8:
            status = ComplianceStatus.COMPLIANT
            findings = [f"All requirements met for {regulation['name']}"]
            required_actions = []
        elif compliance_rate > 0.5:
            status = ComplianceStatus.PENDING_REVIEW
            findings = [f"Partial compliance with {regulation['name']}", "Missing supporting documentation"]
            required_actions = [
                f"Submit missing documents for {regulation['name']}",
                "Verify supplier certifications",
            ]
        else:
            status = ComplianceStatus.NON_COMPLIANT
            findings = [f"Non-compliance detected: {regulation['name']}"]
            required_actions = regulation["requirements"][:3]
        
        return status, findings, required_actions

    def _status_to_risk(self, status: ComplianceStatus) -> RiskLevel:
        mapping = {
            ComplianceStatus.COMPLIANT: RiskLevel.LOW,
            ComplianceStatus.PENDING_REVIEW: RiskLevel.MEDIUM,
            ComplianceStatus.NON_COMPLIANT: RiskLevel.HIGH,
            ComplianceStatus.EXEMPT: RiskLevel.NEGLIGIBLE,
        }
        return mapping.get(status, RiskLevel.MEDIUM)

    def _get_relevant_documents(self, regulation: Dict, shipment: Shipment) -> List[str]:
        docs = shipment.required_documents.copy()
        if "CBAM" in regulation["name"]:
            docs.append("CBAM_Dependent_Declaration")
        if "EUDR" in regulation["name"]:
            docs.append("EUDR_Due_Diligence_Statement")
        if "SOLAS" in regulation["name"]:
            docs.append("VGM_Certificate")
        return docs

    async def generate_audit_report(self, checks: List[ComplianceCheck]) -> Dict[str, Any]:
        """Generate audit-ready compliance report."""
        compliant = sum(1 for c in checks if c.status == ComplianceStatus.COMPLIANT)
        non_compliant = sum(1 for c in checks if c.status == ComplianceStatus.NON_COMPLIANT)
        pending = sum(1 for c in checks if c.status == ComplianceStatus.PENDING_REVIEW)
        
        total_penalty = sum(
            reg["penalty_usd"] for reg in self.REGULATIONS_DB
            for c in checks if c.regulation_name == reg["name"] and c.status == ComplianceStatus.NON_COMPLIANT
        )
        
        return {
            "report_id": f"AUDIT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_checks": len(checks),
                "compliant": compliant,
                "non_compliant": non_compliant,
                "pending_review": pending,
                "compliance_rate": round(compliant / len(checks), 3) if checks else 0,
                "total_potential_penalty_usd": total_penalty,
            },
            "checks": [c.model_dump() for c in checks],
            "recommendations": [
                "Address all non-compliant items immediately",
                "Submit pending documentation within 48 hours",
                "Schedule follow-up review in 30 days",
            ],
            "audit_trail": f"Generated by {self.agent_name} ({self.agent_id}) at {datetime.utcnow().isoformat()}",
        }

    async def process(self, state: SwarmState) -> SwarmState:
        """Process compliance check request."""
        self.update_health(AgentStatus.BUSY)
        
        context = state.get("context", {})
        shipment_data = context.get("shipment")
        
        if shipment_data:
            shipment = Shipment(**shipment_data)
            checks = await self.validate_shipment(shipment)
            
            checks_dict = {c.check_id: c for c in checks}
            state["compliance_checks"] = {**state.get("compliance_checks", {}), **checks_dict}
            
            # Generate audit report if requested
            if context.get("generate_audit_report", False):
                audit_report = await self.generate_audit_report(checks)
                state.setdefault("final_response", {}).update({
                    "compliance_audit": audit_report,
                })
            
            state.setdefault("final_response", {}).update({
                "compliance_checks": [{
                    "check_id": c.check_id,
                    "regulation": c.regulation_name,
                    "category": c.regulation_category,
                    "status": c.status.value,
                    "risk_level": c.risk_level.value,
                    "findings": c.findings,
                    "required_actions": c.required_actions,
                    "confidence": c.confidence.score if c.confidence else 0,
                } for c in checks],
            })
        
        self.update_health(AgentStatus.IDLE)
        return state
