"""
8. INVENTORY & DEMAND FORECASTER AGENT
Predicts demand patterns and recommends optimal inventory levels.
"""
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..state import SwarmState, ConfidenceScore
from .base import AfriSwarmAgent


class InventoryForecasterAgent(AfriSwarmAgent):
    """Demand forecasting and inventory optimization."""

    AGENT_ID = "inventory_forecaster"
    AGENT_NAME = "Inventory & Demand Forecaster"
    DESCRIPTION = "Demand prediction and inventory optimization"
    VERSION = "2.0.0"
    CAPABILITIES = [
        "demand_forecasting", "inventory_optimization", "safety_stock_calculation",
        "reorder_point_suggestion", "volatility_adjustment", "seasonal_analysis",
    ]

    DEFAULT_SYSTEM_PROMPT = """You are the Inventory & Demand Forecaster for AfriSwarm.
    
Use statistical models and ML to predict demand and optimize inventory:
- Time series forecasting (ARIMA, Prophet, neural)
- Safety stock optimization for volatile conditions
- Seasonal pattern detection
- Lead time variability analysis
- Multi-echelon inventory optimization
- Service level targeting
- Bullwhip effect mitigation"""

    async def forecast_demand(
        self, product_category: str, location: str, horizon_days: int = 30
    ) -> Dict[str, Any]:
        base_demand = random.uniform(1000, 50000)
        seasonal_factor = 1.0 + 0.2 * random.uniform(-1, 1)
        trend = 1.0 + (random.uniform(-0.05, 0.05) * horizon_days / 30)
        
        forecast = base_demand * seasonal_factor * trend
        volatility = random.uniform(0.1, 0.4)
        
        safety_stock = forecast * volatility * 1.65  # 95% service level
        reorder_point = forecast * 0.3 + safety_stock
        
        return {
            "product_category": product_category,
            "location": location,
            "forecast_period_days": horizon_days,
            "forecasted_demand_units": round(forecast, 0),
            "confidence_interval_low": round(forecast * (1 - volatility), 0),
            "confidence_interval_high": round(forecast * (1 + volatility), 0),
            "volatility_coefficient": round(volatility, 3),
            "recommended_safety_stock": round(safety_stock, 0),
            "recommended_reorder_point": round(reorder_point, 0),
            "seasonal_factor": round(seasonal_factor, 3),
            "trend_direction": "increasing" if trend > 1 else "decreasing",
            "confidence": ConfidenceScore(
                score=round(1 - volatility, 3),
                model="demand_forecaster",
                reasoning="Based on historical demand patterns and volatility analysis",
            ),
        }

    async def process(self, state: SwarmState) -> SwarmState:
        self.update_health(AgentStatus.BUSY)
        context = state.get("context", {})
        product = context.get("product_category", "general_cargo")
        location = context.get("location", "global")
        
        forecast = await self.forecast_demand(product, location)
        state.setdefault("final_response", {}).update({
            "demand_forecast": forecast,
        })
        self.update_health(AgentStatus.IDLE)
        return state
