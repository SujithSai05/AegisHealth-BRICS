"""
FastAPI REST API routes for AegisHealth BRICS Resilience Platform.
"""
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException, Body
from aegis.database.db import db
from aegis.ai.forecaster import forecaster
from aegis.ai.early_warning import early_warning
from aegis.ai.redistributor import redistributor
from aegis.ai.federated import federated_server
from aegis.simulator.outbreak_engine import outbreak_engine, SCENARIOS
from aegis.config import MEDICINE_CATALOG
from aegis.models.schemas import (
    Facility, StockoutAlert, TransferRecommendation,
    ForecastResponse, SystemStats, SimulationTriggerRequest
)

api_router = APIRouter(prefix="/api")

@api_router.get("/stats")
def get_system_stats():
    """Returns high-level national resilience indicators, beds, staff, and alert counts."""
    return db.get_system_stats()

@api_router.get("/facilities")
def get_facilities(
    district: Optional[str] = Query(None, description="Filter by district name"),
    status: Optional[str] = Query(None, description="Filter by status: CRITICAL, WARNING, STABLE"),
    fac_type: Optional[str] = Query(None, description="Filter by facility type: PHC, CHC, DH")
):
    """Returns list of healthcare facilities with live beds, staffing, and inventory."""
    return db.get_facilities(district=district, status=status, fac_type=fac_type)

@api_router.get("/facilities/{facility_id}")
def get_facility_detail(facility_id: str):
    """Returns comprehensive details for a specific healthcare facility."""
    fac = db.get_facility_by_id(facility_id)
    if not fac:
        raise HTTPException(status_code=404, detail="Facility not found")
    return fac

@api_router.get("/alerts")
def get_alerts(severity: Optional[str] = Query(None, description="Filter by CRITICAL, WARNING")):
    """Returns real-time stockout and bed crisis alerts across the network."""
    return db.get_alerts(severity=severity)

@api_router.post("/alerts/{alert_id}/notify")
def dispatch_alert_notification(alert_id: str):
    """Simulates automated emergency dispatch notification to health officials."""
    return early_warning.simulate_dispatch_notification(alert_id)

@api_router.get("/forecast")
def get_demand_forecast(
    item_id: str = Query("MED-004", description="Medicine catalog ID"),
    horizon_days: int = Query(14, ge=7, le=30, description="Forecast horizon in days"),
    facility_id: Optional[str] = Query(None, description="Facility ID or 'NATIONAL_AGGREGATE'")
):
    """Generates ML demand forecast with confidence intervals and surge risk index."""
    return forecaster.forecast_demand(item_id=item_id, horizon_days=horizon_days, facility_id=facility_id)

@api_router.get("/redistribution/recommendations")
def get_redistribution_recommendations():
    """Computes AI-optimized cross-district and intra-district resource rebalancing transfers."""
    recommendations = redistributor.optimize_redistribution()
    return recommendations

@api_router.post("/redistribution/dispatch")
def dispatch_transfer(
    transfer_id: Optional[str] = Query(None, description="Specific transfer ID to dispatch"),
    auto_all: bool = Query(False, description="Auto-dispatch all recommended transfers")
):
    """Dispatches transfer orders and applies inventory rebalancing."""
    if auto_all:
        recs = redistributor.optimize_redistribution()
        dispatched = redistributor.auto_dispatch_all(recs)
        return {"status": "SUCCESS", "dispatched_count": len(dispatched), "transfers": dispatched}

    if transfer_id:
        result = db.update_transfer_status(transfer_id, "DISPATCHED")
        if not result:
            raise HTTPException(status_code=404, detail="Transfer ID not found")
        return {"status": "SUCCESS", "transfer": result}

    raise HTTPException(status_code=400, detail="Specify transfer_id or set auto_all=true")

@api_router.get("/transfers")
def get_transfers():
    """Lists all active and historical transfer manifests."""
    return db.get_transfers()

@api_router.get("/federated/nodes")
def get_federated_nodes():
    """Returns status and telemetry of all BRICS alliance member nodes."""
    return federated_server.get_alliance_nodes()

@api_router.get("/federated/metrics")
def get_federated_metrics():
    """Returns multi-round convergence metrics, loss history, and differential privacy guarantees."""
    return federated_server.get_federated_metrics()

@api_router.post("/federated/train-round")
def run_federated_round():
    """Triggers a new Federated Averaging (FedAvg) training round across online BRICS nodes."""
    result = federated_server.run_federated_round()
    return result

@api_router.get("/simulation/scenarios")
def get_simulation_scenarios():
    """Returns the list of available crisis simulation scenarios."""
    return SCENARIOS

@api_router.post("/simulation/trigger")
def trigger_simulation(req: SimulationTriggerRequest):
    """Triggers an outbreak crisis simulation or resets the system."""
    result = outbreak_engine.trigger_scenario(req.scenario_id, req.intensity)
    return result

@api_router.get("/catalog")
def get_medicine_catalog():
    """Returns the master essential medicines catalog."""
    return MEDICINE_CATALOG
