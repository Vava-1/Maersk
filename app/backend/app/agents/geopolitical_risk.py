"""
3. GEOPOLITICAL & DISRUPTION RISK MONITOR AGENT
Continuously scans global news, geopolitics, weather, port status, tariffs, and conflicts.
Predicts disruption probability and business impact.
"""
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..state import (
    SwarmState, DisruptionEvent, RiskLevel, ConfidenceScore,
    RouteAlternative, AgentMessage, TaskPriority
)
from .base import AfriSwarmAgent


class GeopoliticalRiskAgent(AfriSwarmAgent):
    """Monitors global risks and disruptions affecting shipping routes."""

    AGENT_ID = "geopolitical_risk"
    AGENT_NAME = "Geopolitical Risk Monitor"
    DESCRIPTION = "Global risk scanner and disruption predictor"
    VERSION = "2.1.0"
    CAPABILITIES = [
        "global_news_monitoring",
        "geopolitical_risk_assessment",
        "weather_event_tracking",
        "port_status_monitoring",
        "tariff_change_detection",
        "conflict_zone_mapping",
        "disruption_probability_prediction",
        "business_impact_quantification",
        "early_warning_generation",
    ]

    DEFAULT_SYSTEM_PROMPT = """You are the Geopolitical Risk Monitor for AfriSwarm.
    
You continuously monitor:
- Global shipping lanes for geopolitical tensions
- Weather patterns and extreme events
- Port closures, congestion, and labor actions
- Tariff changes and trade policy shifts
- Armed conflicts, piracy, and terrorism
- Sanctions and embargo changes
- Pandemic and health-related disruptions

For each detected risk:
1. Assess probability (0.0-1.0)
2. Quantify business impact in USD
3. Estimate duration
4. Identify affected routes and regions
5. Generate specific mitigation recommendations
6. Provide confidence score with reasoning

Priority regions: Red Sea, Suez, Panama, Malacca, Gulf of Guinea,
South China Sea, East African corridor, Mediterranean."""

    # Risk database - production would use real-time feeds
    RISK_EVENTS_DB = [
        {
            "type": "conflict",
            "title": "Red Sea Shipping Crisis",
            "description": "Houthi attacks on commercial vessels in the Red Sea and Gulf of Aden",
            "regions": ["Red Sea", "Gulf of Aden", "Suez Canal"],
            "routes": ["asia_europe_suez", "red_sea_transit"],
            "probability": 0.85,
            "impact_usd": 500000000,
            "duration_days": 180,
            "mitigations": [
                "Route via Cape of Good Hope - add 10-14 days",
                "Increase war risk insurance coverage",
                "Consider air freight for critical cargo",
                "Monitor US/UK naval escort operations",
            ],
        },
        {
            "type": "weather",
            "title": "Cape of Good Hope Weather Advisory",
            "description": "Severe winter storms expected, wave heights 8-12m",
            "regions": ["Cape of Good Hope", "Southern Ocean"],
            "routes": ["asia_europe_cape", "cape_route_all"],
            "probability": 0.60,
            "impact_usd": 25000000,
            "duration_days": 14,
            "mitigations": [
                "Delay departure 48-72 hours for weather window",
                "Ensure vessel structural integrity certified",
                "Monitor real-time weather satellite data",
            ],
        },
        {
            "type": "port_closure",
            "title": "Port of Durban Operational Delays",
            "description": "Equipment failures and congestion causing 5-7 day delays",
            "regions": ["Durban", "South Africa"],
            "routes": ["africa_south_corridor"],
            "probability": 0.70,
            "impact_usd": 15000000,
            "duration_days": 21,
            "mitigations": [
                "Divert to Port Elizabeth or Cape Town",
                "Coordinate with local agents for priority berthing",
                "Consider Maputo as alternative for Mozambique-bound cargo",
            ],
        },
        {
            "type": "conflict",
            "title": "Gulf of Guinea Piracy Alert",
            "description": "Increased pirate activity 200nm off Nigerian coast",
            "regions": ["Gulf of Guinea", "Nigeria", "Benin"],
            "routes": ["west_africa_route"],
            "probability": 0.55,
            "impact_usd": 80000000,
            "duration_days": 90,
            "mitigations": [
                "Vessel hardening measures",
                "Private maritime security team embarkation",
                "Follow BMP5 West Africa guidelines",
                "Register with MDAT-GoG",
            ],
        },
        {
            "type": "regulatory",
            "title": "EU Carbon Border Adjustment (CBAM) Phase-In",
            "description": "CBAM reporting requirements expanding to cover all imports",
            "regions": ["European Union"],
            "routes": ["all_eu_destinations"],
            "probability": 0.95,
            "impact_usd": 120000000,
            "duration_days": 365,
            "mitigations": [
                "Audit supply chain carbon footprint",
                "Switch to green shipping carriers",
                "Invest in offsetting programs",
                "Prepare CBAM documentation templates",
            ],
        },
        {
            "type": "conflict",
            "title": "Sudan Civil War Spillover",
            "description": "Conflict affecting Port Sudan and Red Sea northern access",
            "regions": ["Sudan", "Red Sea North", "Egypt"],
            "routes": ["red_sea_transit"],
            "probability": 0.40,
            "impact_usd": 45000000,
            "duration_days": 365,
            "mitigations": [
                "Avoid Port Sudan - use Jeddah or Aqaba alternatives",
                "Monitor refugee flows affecting logistics",
                "Check cargo insurance coverage exclusions",
            ],
        },
        {
            "type": "weather",
            "title": "El Niño Impact on Panama Canal",
            "description": "Reduced water levels limiting Panama Canal transits",
            "regions": ["Panama Canal", "Central America"],
            "routes": ["asia_east_coast_panama", "panamax_all"],
            "probability": 0.75,
            "impact_usd": 200000000,
            "duration_days": 120,
            "mitigations": [
                "Book transit slots well in advance",
                "Consider Suez routing for Asia-ECNA",
                "Use Neo-Panamax or smaller vessels",
                "Explore US West Coast + rail alternatives",
            ],
        },
        {
            "type": "pandemic",
            "title": "H5N1 Avian Influenza Port Restrictions",
            "description": "Enhanced biosecurity checks at major poultry export ports",
            "regions": ["Brazil", "Southeast Asia"],
            "routes": ["agricultural_exports"],
            "probability": 0.35,
            "impact_usd": 30000000,
            "duration_days": 180,
            "mitigations": [
                "Ensure health certificates in order",
                "Allow extra time for inspections",
                "Monitor WHO and OIE updates",
            ],
        },
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._active_events: List[DisruptionEvent] = []
        self._risk_history: List[Dict] = []
        self.logger.info("Geopolitical Risk Monitor initialized")

    async def scan_global_risks(self) -> List[DisruptionEvent]:
        """Scan for global risks and return active disruption events."""
        self.logger.info("Scanning global risks")
        
        events = []
        for risk_data in self.RISK_EVENTS_DB:
            # Simulate probability fluctuation
            current_probability = min(1.0, max(0.0, risk_data["probability"] + random.uniform(-0.1, 0.1)))
            
            risk_level = self._calculate_risk_level(current_probability, risk_data["impact_usd"])
            
            event = DisruptionEvent(
                event_type=risk_data["type"],
                title=risk_data["title"],
                description=risk_data["description"],
                affected_regions=risk_data["regions"],
                affected_routes=risk_data["routes"],
                risk_level=risk_level,
                probability=round(current_probability, 3),
                estimated_impact_usd=risk_data["impact_usd"],
                estimated_duration_hours=risk_data["duration_days"] * 24,
                mitigation_recommendations=risk_data["mitigations"],
                confidence=ConfidenceScore(
                    score=0.85 if risk_data["probability"] > 0.7 else 0.70,
                    model="risk_scanner_v2",
                    reasoning=f"Based on current {risk_data['type']} indicators",
                ),
                is_active=current_probability > 0.3,
            )
            events.append(event)

        self._active_events = [e for e in events if e.is_active]
        self.logger.info(f"Risk scan complete: {len(self._active_events)} active events")
        return self._active_events

    def _calculate_risk_level(self, probability: float, impact_usd: float) -> RiskLevel:
        """Calculate risk level from probability and impact."""
        score = probability * (min(impact_usd, 1000000000) / 1000000000)
        if score > 0.7:
            return RiskLevel.CRITICAL
        elif score > 0.4:
            return RiskLevel.HIGH
        elif score > 0.2:
            return RiskLevel.MEDIUM
        elif score > 0.05:
            return RiskLevel.LOW
        return RiskLevel.NEGLIGIBLE

    async def assess_route_risk(self, route: RouteAlternative) -> Dict[str, Any]:
        """Assess risk for a specific route."""
        self.logger.info("Assessing route risk", route=f"{route.origin}->{route.destination}")
        
        # Find relevant events
        relevant_events = [
            e for e in self._active_events
            if any(region in route.waypoints for region in e.affected_regions)
            or any(r in e.affected_routes for r in [route.origin, route.destination])
        ]
        
        total_probability = 1.0
        total_impact = 0
        all_mitigations = []
        
        for event in relevant_events:
            total_probability *= (1 - event.probability)
            total_impact += event.estimated_impact_usd
            all_mitigations.extend(event.mitigation_recommendations)
        
        cumulative_probability = 1 - total_probability if relevant_events else 0.0
        
        # Adjust route risk score
        adjusted_risk = min(1.0, route.risk_score + cumulative_probability * 0.3)
        
        return {
            "route_id": route.route_id,
            "adjusted_risk_score": round(adjusted_risk, 3),
            "disruption_probability": round(cumulative_probability, 3),
            "estimated_impact_usd": total_impact,
            "relevant_events": [e.event_id for e in relevant_events],
            "mitigations": list(set(all_mitigations))[:10],
            "confidence": 0.82,
            "recommendation": self._generate_risk_recommendation(adjusted_risk, cumulative_probability),
        }

    def _generate_risk_recommendation(self, risk_score: float, disruption_prob: float) -> str:
        """Generate human-readable risk recommendation."""
        if risk_score > 0.8:
            return "EXTREME RISK - Avoid this route. Select alternative immediately."
        elif risk_score > 0.6:
            return "HIGH RISK - Only use with full mitigation measures and insurance."
        elif risk_score > 0.4:
            return "MODERATE RISK - Implement recommended mitigations and monitor closely."
        elif risk_score > 0.2:
            return "LOW RISK - Standard monitoring sufficient."
        return "MINIMAL RISK - Route is safe for transit."

    async def process(self, state: SwarmState) -> SwarmState:
        """Process risk monitoring cycle."""
        self.update_health(AgentStatus.BUSY)
        
        # Scan for risks
        active_events = await self.scan_global_risks()
        
        # Store in state
        events_dict = {e.event_id: e for e in active_events}
        state["disruption_events"] = {**state.get("disruption_events", {}), **events_dict}
        
        # Generate early warnings
        warnings = self._generate_warnings(active_events)
        state.setdefault("active_alerts", []).extend(warnings)
        
        self.update_health(AgentStatus.IDLE)
        return state

    def _generate_warnings(self, events: List[DisruptionEvent]) -> List[Dict]:
        """Generate early warning alerts."""
        warnings = []
        for event in events:
            if event.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                warnings.append({
                    "type": "risk_warning",
                    "severity": event.risk_level.value,
                    "title": event.title,
                    "description": event.description,
                    "regions": event.affected_regions,
                    "probability": event.probability,
                    "impact_usd": event.estimated_impact_usd,
                    "mitigations": event.mitigation_recommendations[:3],
                    "timestamp": datetime.utcnow().isoformat(),
                })
        return warnings
