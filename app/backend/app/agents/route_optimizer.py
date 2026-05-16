"""
4. ROUTE & LOGISTICS OPTIMIZER AGENT
Optimizes routes considering cost, time, emissions, risk, capacity, and regulations.
"""
import random
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ..state import (
    SwarmState, RouteAlternative, TransportMode, Shipment,
    ConfidenceScore, AgentMessage, TaskPriority
)
from .base import AfriSwarmAgent


class RouteOptimizerAgent(AfriSwarmAgent):
    """Multi-modal route optimization with comprehensive cost/risk/emissions analysis."""

    AGENT_ID = "route_optimizer"
    AGENT_NAME = "Route & Logistics Optimizer"
    DESCRIPTION = "Multi-modal route optimization engine"
    VERSION = "2.2.0"
    CAPABILITIES = [
        "multi_modal_routing",
        "cost_optimization",
        "time_optimization",
        "emissions_minimization",
        "risk_weighted_routing",
        "capacity_planning",
        "regulatory_compliance_check",
        "real_time_rerouting",
        "route_comparison",
        "carrier_selection",
    ]

    DEFAULT_SYSTEM_PROMPT = """You are the Route & Logistics Optimizer for AfriSwarm.
    
Optimize global shipping routes considering ALL factors:
1. Cost: fuel, tolls, port fees, insurance, handling
2. Time: transit duration, port turnaround, customs clearance
3. Emissions: CO2, NOx, SOx per route segment
4. Risk: piracy, weather, geopolitical, congestion
5. Capacity: vessel/container availability
6. Regulations: ballast water, emissions zones, cabotage
7. Reliability: carrier on-time performance history

For each routing request:
- Generate at least 3 alternative routes
- Score each on multi-dimensional Pareto front
- Provide confidence intervals for all estimates
- Include sensitivity analysis for key assumptions
- Recommend optimal with full reasoning trace

Special expertise:
- Africa corridors: Mombasa-Nairobi, Lagos-Accra, Dar es Salaam-Lusaka
- Red Sea alternatives via Cape of Good Hope
- Suez vs Panama trade-offs
- Multimodal: sea-rail-road combinations"""

    # Route database for demo
    ROUTE_DATABASE = {
        # Asia-Europe via Suez
        "asia_europe_suez": {
            "origin": "Shanghai", "destination": "Rotterdam",
            "waypoints": ["Shanghai", "Singapore", "Colombo", "Suez Canal", "Rotterdam"],
            "modes": [TransportMode.SEA, TransportMode.SEA, TransportMode.SEA],
            "base_cost_usd": 2850, "base_hours": 504, "base_co2_kg": 4200,
            "base_risk": 0.35, "carrier_reliability": 0.92,
        },
        # Asia-Europe via Cape
        "asia_europe_cape": {
            "origin": "Shanghai", "destination": "Rotterdam",
            "waypoints": ["Shanghai", "Singapore", "Durban", "Cape of Good Hope", "Rotterdam"],
            "modes": [TransportMode.SEA, TransportMode.SEA, TransportMode.SEA],
            "base_cost_usd": 3200, "base_hours": 696, "base_co2_kg": 5800,
            "base_risk": 0.15, "carrier_reliability": 0.88,
        },
        # Asia-East Coast NA via Panama
        "asia_east_coast_panama": {
            "origin": "Shanghai", "destination": "New York",
            "waypoints": ["Shanghai", "Busan", "Panama Canal", "New York"],
            "modes": [TransportMode.SEA, TransportMode.SEA, TransportMode.SEA],
            "base_cost_usd": 3100, "base_hours": 552, "base_co2_kg": 4800,
            "base_risk": 0.25, "carrier_reliability": 0.90,
        },
        # East Africa corridor
        "mombasa_nairobi_addis": {
            "origin": "Mombasa", "destination": "Addis Ababa",
            "waypoints": ["Mombasa", "Nairobi", "Moyale", "Addis Ababa"],
            "modes": [TransportMode.SEA, TransportMode.ROAD, TransportMode.ROAD],
            "base_cost_usd": 1850, "base_hours": 96, "base_co2_kg": 890,
            "base_risk": 0.30, "carrier_reliability": 0.72,
        },
        # West Africa corridor
        "lagos_accra_abidjan": {
            "origin": "Lagos", "destination": "Abidjan",
            "waypoints": ["Lagos", "Accra", "Abidjan"],
            "modes": [TransportMode.ROAD, TransportMode.ROAD],
            "base_cost_usd": 920, "base_hours": 36, "base_co2_kg": 450,
            "base_risk": 0.28, "carrier_reliability": 0.68,
        },
        # Southern Africa corridor
        "dar_es_salaam_lusaka": {
            "origin": "Dar es Salaam", "destination": "Lusaka",
            "waypoints": ["Dar es Salaam", "Mbeya", "Nakonde", "Lusaka"],
            "modes": [TransportMode.SEA, TransportMode.RAIL, TransportMode.RAIL],
            "base_cost_usd": 2100, "base_hours": 120, "base_co2_kg": 1200,
            "base_risk": 0.22, "carrier_reliability": 0.65,
        },
        # Europe-West Africa
        "europe_west_africa": {
            "origin": "Rotterdam", "destination": "Lagos",
            "waypoints": ["Rotterdam", "Algeciras", "Lagos"],
            "modes": [TransportMode.SEA, TransportMode.SEA],
            "base_cost_usd": 2400, "base_hours": 288, "base_co2_kg": 3200,
            "base_risk": 0.20, "carrier_reliability": 0.85,
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger.info("Route Optimizer initialized")

    async def generate_route_alternatives(
        self,
        origin: str,
        destination: str,
        shipment: Optional[Shipment] = None,
        constraints: Optional[Dict] = None,
    ) -> List[RouteAlternative]:
        """Generate optimized route alternatives."""
        self.logger.info("Generating routes", origin=origin, destination=destination)
        
        constraints = constraints or {}
        max_risk = constraints.get("max_risk", 1.0)
        max_cost = constraints.get("max_cost_usd", float("inf"))
        max_time = constraints.get("max_hours", float("inf"))
        prefer_green = constraints.get("prefer_green", False)
        
        # Find matching routes from database
        matching_routes = []
        for route_id, route_data in self.ROUTE_DATABASE.items():
            if (route_data["origin"].lower() in origin.lower() or 
                origin.lower() in route_data["origin"].lower()) and \
               (route_data["destination"].lower() in destination.lower() or
                destination.lower() in route_data["destination"].lower()):
                matching_routes.append((route_id, route_data))
        
        # If no direct match, generate a generic route
        if not matching_routes:
            matching_routes = await self._generate_generic_route(origin, destination)
        
        # Build RouteAlternative objects with variations
        alternatives = []
        for route_id, route_data in matching_routes:
            # Create base route
            base = self._build_route(route_id, route_data, "standard")
            if self._meets_constraints(base, max_risk, max_cost, max_time):
                alternatives.append(base)
            
            # Create cost-optimized variant
            cost_opt = self._build_route(route_id, route_data, "cost_optimized")
            if cost_opt and self._meets_constraints(cost_opt, max_risk, max_cost, max_time):
                alternatives.append(cost_opt)
            
            # Create time-optimized variant
            time_opt = self._build_route(route_id, route_data, "time_optimized")
            if time_opt and self._meets_constraints(time_opt, max_risk, max_cost, max_time):
                alternatives.append(time_opt)
            
            # Create green variant if preferred
            if prefer_green or constraints.get("emissions_weight", 0) > 0.3:
                green = self._build_route(route_id, route_data, "green")
                if green and self._meets_constraints(green, max_risk, max_cost, max_time):
                    alternatives.append(green)
        
        # Score and rank
        scored = self._score_routes(alternatives, constraints)
        scored.sort(key=lambda x: x["composite_score"], reverse=True)
        
        # Return top routes
        result = [s["route"] for s in scored[:5]]
        self.logger.info(f"Generated {len(result)} route alternatives")
        return result

    def _build_route(
        self,
        route_id: str,
        route_data: Dict,
        variant: str,
    ) -> RouteAlternative:
        """Build a route variant with modified parameters."""
        # Apply variant modifiers
        cost_mult, time_mult, co2_mult, risk_mult = 1.0, 1.0, 1.0, 1.0
        
        if variant == "cost_optimized":
            cost_mult = 0.85
            time_mult = 1.15
            co2_mult = 1.05
        elif variant == "time_optimized":
            cost_mult = 1.20
            time_mult = 0.80
            co2_mult = 1.10
        elif variant == "green":
            cost_mult = 1.10
            time_mult = 1.05
            co2_mult = 0.70
        
        # Add random variation for realism
        cost_mult *= random.uniform(0.95, 1.05)
        time_mult *= random.uniform(0.95, 1.05)
        co2_mult *= random.uniform(0.95, 1.05)
        
        route = RouteAlternative(
            origin=route_data["origin"],
            destination=route_data["destination"],
            waypoints=route_data["waypoints"],
            transport_modes=route_data["modes"],
            estimated_cost_usd=round(route_data["base_cost_usd"] * cost_mult, 2),
            estimated_duration_hours=round(route_data["base_hours"] * time_mult, 1),
            estimated_co2_kg=round(route_data["base_co2_kg"] * co2_mult, 2),
            risk_score=round(min(1.0, route_data["base_risk"] * risk_mult), 3),
            disruption_probability=round(route_data["base_risk"] * random.uniform(0.8, 1.2), 3),
            carrier_reliability_score=route_data["carrier_reliability"],
            current_status=f"{variant}_available",
            advantages=self._get_advantages(variant),
            disadvantages=self._get_disadvantages(variant),
        )
        return route

    def _get_advantages(self, variant: str) -> List[str]:
        advantages = {
            "standard": ["Balanced cost and time", "Proven reliability"],
            "cost_optimized": ["Lowest freight cost", "Good for non-urgent cargo"],
            "time_optimized": ["Fastest delivery", "Minimizes inventory carrying cost"],
            "green": ["Lowest carbon footprint", "ESG compliant", "Future-proof against regulations"],
        }
        return advantages.get(variant, ["Standard routing"])

    def _get_disadvantages(self, variant: str) -> List[str]:
        disadvantages = {
            "standard": ["Not optimized for any specific dimension"],
            "cost_optimized": ["Longer transit time", "Potential for lower service quality"],
            "time_optimized": ["Higher cost", "May require premium carriers"],
            "green": ["Higher cost", "Limited carrier options", "Potentially longer routes"],
        }
        return disadvantages.get(variant, [])

    def _meets_constraints(
        self, route: RouteAlternative,
        max_risk: float, max_cost: float, max_time: float
    ) -> bool:
        return (route.risk_score <= max_risk and
                route.estimated_cost_usd <= max_cost and
                route.estimated_duration_hours <= max_time)

    def _score_routes(
        self,
        routes: List[RouteAlternative],
        constraints: Dict,
    ) -> List[Dict]:
        """Score routes using weighted multi-criteria analysis."""
        # Weights from constraints or defaults
        w_cost = constraints.get("cost_weight", 0.25)
        w_time = constraints.get("time_weight", 0.25)
        w_emissions = constraints.get("emissions_weight", 0.20)
        w_risk = constraints.get("risk_weight", 0.20)
        w_reliability = constraints.get("reliability_weight", 0.10)
        
        scored = []
        for route in routes:
            # Normalize scores (lower is better for cost, time, emissions, risk)
            norm_cost = 1.0 - min(1.0, route.estimated_cost_usd / 10000)
            norm_time = 1.0 - min(1.0, route.estimated_duration_hours / 1000)
            norm_emissions = 1.0 - min(1.0, route.estimated_co2_kg / 10000)
            norm_risk = 1.0 - route.risk_score
            norm_reliability = route.carrier_reliability_score
            
            composite = (
                norm_cost * w_cost +
                norm_time * w_time +
                norm_emissions * w_emissions +
                norm_risk * w_risk +
                norm_reliability * w_reliability
            )
            
            scored.append({
                "route": route,
                "composite_score": round(composite, 4),
                "normalized": {
                    "cost": round(norm_cost, 3),
                    "time": round(norm_time, 3),
                    "emissions": round(norm_emissions, 3),
                    "risk": round(norm_risk, 3),
                    "reliability": round(norm_reliability, 3),
                },
            })
        
        return scored

    async def _generate_generic_route(
        self, origin: str, destination: str
    ) -> List[Tuple[str, Dict]]:
        """Generate a generic route when no database match exists."""
        distance_factor = random.uniform(0.8, 1.5)
        route_data = {
            "origin": origin, "destination": destination,
            "waypoints": [origin, "Intermediate Hub", destination],
            "modes": [TransportMode.MULTIMODAL],
            "base_cost_usd": round(2000 * distance_factor, 2),
            "base_hours": round(400 * distance_factor, 1),
            "base_co2_kg": round(3500 * distance_factor, 2),
            "base_risk": round(0.25 * random.uniform(0.8, 1.5), 3),
            "carrier_reliability": round(random.uniform(0.70, 0.95), 3),
        }
        return [("generic", route_data)]

    async def process(self, state: SwarmState) -> SwarmState:
        """Process route optimization request."""
        self.update_health(AgentStatus.BUSY)
        
        # Check for shipment data in context
        context = state.get("context", {})
        shipment_data = context.get("shipment")
        
        if shipment_data:
            origin = shipment_data.get("origin", "")
            destination = shipment_data.get("destination", "")
            shipment = Shipment(**shipment_data) if isinstance(shipment_data, dict) else None
        else:
            # Extract from query
            query = state.get("user_query", "")
            origin, destination = self._extract_locations(query)
            shipment = None
        
        if origin and destination:
            constraints = context.get("constraints", {})
            alternatives = await self.generate_route_alternatives(
                origin, destination, shipment, constraints
            )
            
            # Store in state
            routes_dict = {r.route_id: r for r in alternatives}
            state["route_alternatives"] = {**state.get("route_alternatives", {}), **routes_dict}
            
            # Add to response
            state.setdefault("final_response", {}).update({
                "route_alternatives": [{
                    "route_id": r.route_id,
                    "origin": r.origin,
                    "destination": r.destination,
                    "waypoints": r.waypoints,
                    "cost_usd": r.estimated_cost_usd,
                    "duration_hours": r.estimated_duration_hours,
                    "co2_kg": r.estimated_co2_kg,
                    "risk_score": r.risk_score,
                    "reliability": r.carrier_reliability_score,
                    "advantages": r.advantages,
                    "disadvantages": r.disadvantages,
                } for r in alternatives],
            })
        
        self.update_health(AgentStatus.IDLE)
        return state

    def _extract_locations(self, query: str) -> Tuple[str, str]:
        """Extract origin and destination from natural language query."""
        query_lower = query.lower()
        
        # Common pattern matching
        import re
        patterns = [
            r'from\s+([\w\s]+?)\s+to\s+([\w\s]+)',
            r'route\s+from\s+([\w\s]+?)\s+to\s+([\w\s]+)',
            r'ship\s+from\s+([\w\s]+?)\s+to\s+([\w\s]+)',
            r'([\w\s]+?)\s+to\s+([\w\s]+)\s+route',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                return match.group(1).strip().title(), match.group(2).strip().title()
        
        return "", ""
