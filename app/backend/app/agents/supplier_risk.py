"""
7. SUPPLIER RISK & PERFORMANCE AGENT
Monitors multi-tier suppliers for financial health, reliability, capacity, and risks.
"""
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..state import SwarmState, SupplierRiskProfile, RiskLevel, ConfidenceScore
from .base import AfriSwarmAgent


class SupplierRiskAgent(AfriSwarmAgent):
    """Multi-tier supplier risk and performance monitoring."""

    AGENT_ID = "supplier_risk"
    AGENT_NAME = "Supplier Risk & Performance Agent"
    DESCRIPTION = "Supplier monitoring and risk assessment"
    VERSION = "2.0.0"
    CAPABILITIES = [
        "financial_health_assessment", "reliability_tracking", "capacity_monitoring",
        "esg_scoring", "geopolitical_exposure", "diversification_recommendations",
    ]

    DEFAULT_SYSTEM_PROMPT = """You are the Supplier Risk & Performance Agent for AfriSwarm.
    
Monitor suppliers across:
- Financial health (credit rating, payment history, liquidity)
- Operational reliability (on-time delivery, quality defects)
- Capacity utilization and expansion capability
- ESG performance
- Geopolitical risk exposure
- Concentration risk in supply base
- Sub-tier supplier mapping

Provide diversification recommendations and early warnings."""

    SUPPLIER_DB = {
        "MAEU_SHANGHAI": {"name": "Shanghai Port Services", "country": "CN", 
                         "financial": 0.88, "reliability": 0.92, "capacity": 0.75, "esg": 0.65},
        "MAEU_DURBAN": {"name": "Durban Container Terminal", "country": "ZA",
                        "financial": 0.72, "reliability": 0.78, "capacity": 0.85, "esg": 0.70},
        "MAEU_LAGOS": {"name": "Lagos Port Complex", "country": "NG",
                       "financial": 0.58, "reliability": 0.65, "capacity": 0.90, "esg": 0.55},
        "MAEU_MOMBASA": {"name": "Mombasa Port Authority", "country": "KE",
                         "financial": 0.68, "reliability": 0.72, "capacity": 0.80, "esg": 0.60},
        "MAEU_ROTTERDAM": {"name": "Rotterdam World Gateway", "country": "NL",
                           "financial": 0.95, "reliability": 0.96, "capacity": 0.70, "esg": 0.88},
        "MAEU_SINGAPORE": {"name": "PSA Singapore", "country": "SG",
                           "financial": 0.93, "reliability": 0.94, "capacity": 0.80, "esg": 0.82},
    }

    async def assess_supplier(self, supplier_id: str) -> SupplierRiskProfile:
        data = self.SUPPLIER_DB.get(supplier_id, {
            "name": f"Supplier_{supplier_id}", "country": "Unknown",
            "financial": 0.70, "reliability": 0.70, "capacity": 0.70, "esg": 0.60,
        })
        
        geo_risk = self._country_risk_score(data["country"])
        overall = self._calculate_overall_risk(data, geo_risk)
        
        return SupplierRiskProfile(
            supplier_id=supplier_id,
            supplier_name=data["name"],
            country=data["country"],
            risk_level=overall,
            financial_health_score=data["financial"],
            reliability_score=data["reliability"],
            capacity_utilization=data["capacity"],
            esg_score=data["esg"],
            geopolitical_risk_exposure=geo_risk,
            diversification_recommendations=self._get_diversification(data, supplier_id),
            risk_factors=self._get_risk_factors(data, geo_risk),
        )

    def _country_risk_score(self, country: str) -> float:
        scores = {"CN": 0.35, "ZA": 0.45, "NG": 0.65, "KE": 0.50, "NL": 0.15, "SG": 0.20,
                 "US": 0.20, "DE": 0.15, "GB": 0.22, "IN": 0.40, "BR": 0.42}
        return scores.get(country, 0.50)

    def _calculate_overall_risk(self, data: Dict, geo_risk: float) -> RiskLevel:
        avg = (data["financial"] + data["reliability"] + (1-data["capacity"])*0.5 + data["esg"]) / 3.5
        weighted = avg * 0.7 + (1-geo_risk) * 0.3
        if weighted < 0.4: return RiskLevel.CRITICAL
        elif weighted < 0.55: return RiskLevel.HIGH
        elif weighted < 0.70: return RiskLevel.MEDIUM
        elif weighted < 0.85: return RiskLevel.LOW
        return RiskLevel.NEGLIGIBLE

    def _get_diversification(self, data: Dict, supplier_id: str) -> List[str]:
        recs = ["Develop alternative supplier relationships"]
        if data["capacity"] > 0.85:
            recs.append("Supplier near capacity - identify overflow options")
        if data["financial"] < 0.65:
            recs.append("Financial stress detected - reduce exposure")
        return recs

    def _get_risk_factors(self, data: Dict, geo_risk: float) -> List[str]:
        factors = []
        if data["financial"] < 0.65: factors.append("Financial instability")
        if data["reliability"] < 0.75: factors.append("Delivery unreliability")
        if geo_risk > 0.5: factors.append("High geopolitical exposure")
        if data["esg"] < 0.60: factors.append("ESG concerns")
        return factors or ["No critical risk factors identified"]

    async def process(self, state: SwarmState) -> SwarmState:
        self.update_health(AgentStatus.BUSY)
        context = state.get("context", {})
        supplier_id = context.get("supplier_id", "MAEU_SHANGHAI")
        profile = await self.assess_supplier(supplier_id)
        state["supplier_risks"] = {**state.get("supplier_risks", {}), supplier_id: profile}
        self.update_health(AgentStatus.IDLE)
        return state
