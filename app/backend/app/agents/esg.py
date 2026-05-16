"""
6. ESG & SUSTAINABILITY AGENT
Tracks carbon emissions, environmental and social impact.
"""
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..state import SwarmState, ESGMetric, ConfidenceScore, Shipment, RouteAlternative
from .base import AfriSwarmAgent


class ESGAgent(AfriSwarmAgent):
    """Environmental, Social, and Governance tracking and optimization."""

    AGENT_ID = "esg"
    AGENT_NAME = "ESG & Sustainability Agent"
    DESCRIPTION = "Carbon emissions and ESG impact tracking"
    VERSION = "2.0.0"
    CAPABILITIES = [
        "carbon_tracking", "eu_cbam_compliance", "deforestation_monitoring",
        "emissions_optimization", "green_alternatives", "sustainability_reporting",
    ]

    DEFAULT_SYSTEM_PROMPT = """You are the ESG & Sustainability Agent for AfriSwarm.
    
Track and optimize:
- Carbon emissions (CO2, CH4, N2O) per shipment and route
- EU CBAM compliance calculations
- EU Deforestation Regulation (EUDR) status
- Fuel consumption and efficiency metrics
- Green corridor eligibility
- Alternative fuel feasibility (LNG, methanol, ammonia, hydrogen)
- Carbon offset opportunities
- Scope 1, 2, 3 emissions tracking
- Science-Based Targets alignment"""

    async def calculate_shipment_emissions(
        self, shipment: Shipment, route: RouteAlternative
    ) -> List[ESGMetric]:
        """Calculate emissions for a shipment on a route."""
        metrics = []
        
        # CO2 emissions
        co2 = ESGMetric(
            metric_type="carbon",
            shipment_id=shipment.shipment_id,
            value=route.estimated_co2_kg,
            unit="kg CO2e",
            benchmark_value=route.estimated_co2_kg * 1.2,
            reduction_target=route.estimated_co2_kg * 0.3,
            improvement_recommendations=[
                "Consider green corridor routing",
                "Explore LNG-powered vessel options",
                "Evaluate carbon offset purchases",
            ],
            eu_cbam_applicable=shipment.cargo_type.lower() in ["steel", "aluminum", "cement", "fertilizer"],
        )
        metrics.append(co2)
        
        # Fuel efficiency
        fuel_liters = route.estimated_co2_kg / 2.68  # ~2.68 kg CO2 per liter diesel
        efficiency = ESGMetric(
            metric_type="fuel_efficiency",
            shipment_id=shipment.shipment_id,
            value=round(fuel_liters, 2),
            unit="liters",
            benchmark_value=fuel_liters * 1.15,
            reduction_target=fuel_liters * 0.25,
            improvement_recommendations=[
                "Optimize vessel speed for fuel efficiency",
                "Consider slow-steaming on non-urgent cargo",
            ],
        )
        metrics.append(efficiency)
        
        # Social impact score
        social = ESGMetric(
            metric_type="social",
            shipment_id=shipment.shipment_id,
            value=round(random.uniform(0.7, 0.95), 3),
            unit="score",
            benchmark_value=0.75,
            improvement_recommendations=[
                "Verify labor standards in origin port",
                "Check supplier code of conduct compliance",
            ],
        )
        metrics.append(social)
        
        return metrics

    async def process(self, state: SwarmState) -> SwarmState:
        self.update_health(AgentStatus.BUSY)
        
        context = state.get("context", {})
        shipment_data = context.get("shipment")
        route_data = context.get("route")
        
        if shipment_data and route_data:
            shipment = Shipment(**shipment_data)
            route = RouteAlternative(**route_data)
            metrics = await self.calculate_shipment_emissions(shipment, route)
            
            metrics_dict = {m.metric_id: m for m in metrics}
            state["esg_metrics"] = {**state.get("esg_metrics", {}), **metrics_dict}
            
            state.setdefault("final_response", {}).update({
                "esg_metrics": [m.model_dump() for m in metrics],
            })
        
        self.update_health(AgentStatus.IDLE)
        return state
