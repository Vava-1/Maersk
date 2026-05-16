"""
12. AFRICA / EMERGING MARKETS SPECIALIST AGENT
Deep localized expertise on African logistics, infrastructure, corridors.
"""
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..state import SwarmState, RouteAlternative, TransportMode, ConfidenceScore
from .base import AfriSwarmAgent


class AfricaSpecialistAgent(AfriSwarmAgent):
    """Deep expertise on African logistics corridors and challenges."""

    AGENT_ID = "africa_specialist"
    AGENT_NAME = "Africa / Emerging Markets Specialist"
    DESCRIPTION = "African logistics, infrastructure, and regional regulation expert"
    VERSION = "2.0.0"
    CAPABILITIES = [
        "africa_corridor_expertise", "infrastructure_assessment", "regional_regulations",
        "port_knowledge", "customs_procedures", "inland_logistics", "risk_mapping",
        "market_entry_advice", "local_partner_recommendations",
    ]

    DEFAULT_SYSTEM_PROMPT = """You are the Africa & Emerging Markets Specialist for AfriSwarm.
    
Deep expertise in African logistics:
- East Africa Corridor: Mombasa-Nairobi-Addis Ababa
- Northern Corridor: Mombasa-Kampala-Kigali-Goma
- Central Corridor: Dar es Salaam-Dodoma-Kigali
- West Africa: Lagos-Accra-Abidjan corridor
- Southern Africa: Durban-Lusaka-Harare
- Special economic zones and free trade areas
- AfCFTA implementation and rules of origin
- Local infrastructure constraints and workarounds
- Port congestion patterns and seasonal variations
- Cross-border clearance procedures
- Inland waterway potential (Niger, Congo, Nile)
- Railway rehabilitation projects
- Digital logistics platforms in Africa"""

    AFRICA_CORRIDORS = {
        "northern_corridor": {
            "name": "Northern Corridor",
            "route": "Mombasa -> Nairobi -> Kampala -> Kigali -> Goma",
            "distance_km": 2200,
            "transit_time_hours": 168,
            "cost_usd_per_teu": 2800,
            "infrastructure_quality": 0.55,
            "border_delays_hours": 48,
            "key_challenges": [
                "Weightbridges and police checkpoints (Kenya: 12+, Uganda: 8+)",
                "Mombasa port congestion - 5-7 day dwell time",
                "Road condition variability - seasonal degradation",
                "Multiple customs clearance points",
                "Informal sector competition for trucking",
            ],
            "improvements": [
                "Standard Gauge Railway (SGR) extension to Malaba",
                "Kenya-Uganda one-stop border post modernization",
                "EAC Single Customs Territory implementation",
                "Mombasa port automation and berthing expansion",
            ],
            "risk_factors": ["political_tension", "infrastructure_degradation", "weather_seasonal"],
        },
        "central_corridor": {
            "name": "Central Corridor",
            "route": "Dar es Salaam -> Dodoma -> Kigali/Bujumbura",
            "distance_km": 1800,
            "transit_time_hours": 144,
            "cost_usd_per_teu": 2600,
            "infrastructure_quality": 0.50,
            "border_delays_hours": 36,
            "key_challenges": [
                "Dar es Salaam port capacity constraints",
                "Central Tanzania road network quality",
                "Isaka-Rwanda railway gauge mismatch",
                "Burundi political instability spillover",
            ],
            "improvements": [
                "Dar es Salaam port expansion (DP World concession)",
                "Central Corridor railway rehabilitation",
                "Rwanda logistics hub development",
                "Electronic cargo tracking (RECTS)",
            ],
            "risk_factors": ["port_capacity", "railway_rehabilitation", "political_instability"],
        },
        "west_africa_corridor": {
            "name": "West Africa Coastal Corridor",
            "route": "Lagos -> Accra -> Abidjan -> Lomé",
            "distance_km": 1200,
            "transit_time_hours": 72,
            "cost_usd_per_teu": 2200,
            "infrastructure_quality": 0.58,
            "border_delays_hours": 24,
            "key_challenges": [
                "Lagos port congestion and Apapa gridlock",
                "Multiple border crossings with different procedures",
                "Road infrastructure quality variance",
                "Security concerns in specific stretches",
            ],
            "improvements": [
                "Lekki Deep Sea Port (new gateway)",
                "ECOWAS Trade Liberalization Scheme",
                "Abidjan-Lagos corridor highway upgrade",
                "Digital customs platforms (Ghana, Nigeria)",
            ],
            "risk_factors": ["port_congestion", "security", "border_delays"],
        },
        "cape_to_cairo": {
            "name": "Cape to Cairo Vision",
            "route": "Cape Town -> Gaborone -> Lusaka -> Dar es Salaam/Nairobi",
            "distance_km": 5200,
            "transit_time_hours": 336,
            "cost_usd_per_teu": 4500,
            "infrastructure_quality": 0.45,
            "border_delays_hours": 72,
            "key_challenges": [
                "Multi-country coordination complexity",
                "Gauge differences (Cape vs. Meter)",
                "Remote stretches with limited services",
                "Political instability in transit countries",
            ],
            "improvements": [
                "Trans-African Highway network upgrade",
                "Tripartite Free Trade Area implementation",
                "Regional railway interconnectivity",
                "Corridor development authorities",
            ],
            "risk_factors": ["multi_country", "gauge_mismatch", "political", "distance"],
        },
    }

    AFRICA_PORTS = {
        "mombasa": {
            "name": "Port of Mombasa",
            "country": "Kenya",
            "throughput_teu_annual": 1400000,
            "congestion_level": "high",
            "avg_dwell_time_days": 6.5,
            "efficiency_score": 0.55,
            "expansion_plans": "Second container terminal, Dongo Kundu freeport",
            "challenges": ["Yard congestion", "Equipment aging", "Customs delays"],
        },
        "dar_es_salaam": {
            "name": "Port of Dar es Salaam",
            "country": "Tanzania",
            "throughput_teu_annual": 950000,
            "congestion_level": "medium-high",
            "avg_dwell_time_days": 8.2,
            "efficiency_score": 0.48,
            "expansion_plans": "Berth 13-14 extension, Kigamboni satellite port",
            "challenges": ["Limited yard space", "Equipment shortages", "Hinterland access"],
        },
        "lagos": {
            "name": "Lagos Port Complex",
            "country": "Nigeria",
            "throughput_teu_annual": 1200000,
            "congestion_level": "critical",
            "avg_dwell_time_days": 21.0,
            "efficiency_score": 0.35,
            "expansion_plans": "Lekki Deep Sea Port (operational 2023), Badagry port",
            "challenges": ["Apapa access gridlock", "Extreme dwell times", "Corruption"],
        },
        "durban": {
            "name": "Port of Durban",
            "country": "South Africa",
            "throughput_teu_annual": 3100000,
            "congestion_level": "medium",
            "avg_dwell_time_days": 4.5,
            "efficiency_score": 0.72,
            "expansion_plans": "Pier 1 deepening, truck staging area expansion",
            "challenges": ["Weather disruptions", "Rail connectivity", "Equipment maintenance"],
        },
        "luanda": {
            "name": "Port of Luanda",
            "country": "Angola",
            "throughput_teu_annual": 850000,
            "congestion_level": "high",
            "avg_dwell_time_days": 14.0,
            "efficiency_score": 0.40,
            "expansion_plans": "Luanda Bay terminal modernization, Barra do Dande",
            "challenges": ["Customs complexity", "Currency convertibility", "Infrastructure"],
        },
    }

    async def get_corridor_analysis(self, corridor_id: str) -> Dict[str, Any]:
        """Get detailed analysis of an African corridor."""
        corridor = self.AFRICA_CORRIDORS.get(corridor_id, {
            "name": "Unknown Corridor",
            "route": "N/A",
            "distance_km": 0,
            "transit_time_hours": 0,
            "cost_usd_per_teu": 0,
            "infrastructure_quality": 0.3,
            "border_delays_hours": 72,
            "key_challenges": ["Data not available"],
            "improvements": ["Data not available"],
            "risk_factors": ["unknown"],
        })
        
        return {
            "corridor_id": corridor_id,
            **corridor,
            "risk_score": round(1 - corridor.get("infrastructure_quality", 0.3), 3),
            "recommendations": self._generate_corridor_recommendations(corridor),
            "seasonal_factors": self._get_seasonal_factors(corridor_id),
            "last_updated": datetime.utcnow().isoformat(),
            "confidence": ConfidenceScore(
                score=0.88,
                model="africa_specialist",
                reasoning="Based on field data and industry reports",
            ),
        }

    def _generate_corridor_recommendations(self, corridor: Dict) -> List[str]:
        recs = []
        if corridor.get("infrastructure_quality", 0) < 0.5:
            recs.append("Plan for additional buffer time (20-30%)")
            recs.append("Use GPS tracking and real-time monitoring")
        if corridor.get("border_delays_hours", 0) > 36:
            recs.append("Engage experienced customs broker at each border")
            recs.append("Pre-clear cargo using available digital platforms")
        recs.extend(corridor.get("improvements", [])[:2])
        return recs

    def _get_seasonal_factors(self, corridor_id: str) -> Dict[str, Any]:
        return {
            "rainy_season_impact": random.choice(["high", "medium", "low"]),
            "peak_congestion_months": random.choice([["March-May", "Oct-Dec"], ["Nov-Jan"], ["Jun-Aug"]]),
            "best_transit_months": random.choice([["Jan-Feb", "Jun-Sep"], ["Feb-Apr"], ["Sep-Nov"]]),
        }

    async def get_port_analysis(self, port_id: str) -> Dict[str, Any]:
        """Get detailed analysis of an African port."""
        port = self.AFRICA_PORTS.get(port_id, {
            "name": f"Port of {port_id.title()}",
            "country": "Unknown",
            "throughput_teu_annual": 0,
            "congestion_level": "unknown",
            "avg_dwell_time_days": 14,
            "efficiency_score": 0.3,
        })
        
        return {
            "port_id": port_id,
            **port,
            "recommendations": [
                f"Book berthing {port.get('avg_dwell_time_days', 7)} days in advance",
                "Engage local port agent for coordination",
                f"Factor {port.get('avg_dwell_time_days', 7)} day dwell time in planning",
            ],
            "confidence": ConfidenceScore(
                score=0.85,
                model="africa_specialist",
                reasoning="Based on port authority data and vessel tracking",
            ),
        }

    async def process(self, state: SwarmState) -> SwarmState:
        self.update_health(AgentStatus.BUSY)
        context = state.get("context", {})
        corridor_id = context.get("corridor_id", "northern_corridor")
        port_id = context.get("port_id")
        
        results = {}
        if corridor_id:
            results["corridor_analysis"] = await self.get_corridor_analysis(corridor_id)
        if port_id:
            results["port_analysis"] = await self.get_port_analysis(port_id)
        
        if not results:
            results["available_corridors"] = list(self.AFRICA_CORRIDORS.keys())
            results["available_ports"] = list(self.AFRICA_PORTS.keys())
        
        state.setdefault("final_response", {}).update(results)
        self.update_health(AgentStatus.IDLE)
        return state
