"""
Data models and Pydantic schemas for AegisHealth BRICS.
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class MedicineStock(BaseModel):
    id: str
    name: str
    category: str
    unit: str
    current_stock: int
    min_threshold: int
    daily_burn_rate: float
    days_runway: float
    cold_chain: bool = False
    temp_range: Optional[str] = None
    batch_no: str
    expiry_date: str
    status: str = "OPTIMAL" # CRITICAL, WARNING, OPTIMAL, SURPLUS

class BedAvailability(BaseModel):
    total: int
    occupied: int
    available: int
    icu_total: int
    icu_occupied: int
    oxygen_total: int
    oxygen_occupied: int
    general_total: int
    general_occupied: int
    isolation_total: int
    isolation_occupied: int
    occupancy_rate: float

class StaffAttendance(BaseModel):
    doctors_total: int
    doctors_on_duty: int
    nurses_total: int
    nurses_on_duty: int
    pharmacists_on_duty: int
    lab_techs_on_duty: int
    asha_workers_active: int
    attendance_ratio: float
    status: str = "NORMAL" # NORMAL, STRESSED, SEVERE

class Facility(BaseModel):
    id: str
    name: str
    code: str
    type: str # PHC (Primary Health Centre), CHC (Community Health Centre), DH (District Hospital)
    district: str
    state: str
    latitude: float
    longitude: float
    catchment_population: int
    beds: BedAvailability
    staff: StaffAttendance
    inventory: List[MedicineStock]
    overall_status: str = "STABLE" # CRITICAL, WARNING, STABLE
    risk_score: float = 0.0 # 0 to 100
    last_reported: str

class StockoutAlert(BaseModel):
    id: str
    facility_id: str
    facility_name: str
    district: str
    item_id: str
    item_name: str
    category: str
    severity: str # CRITICAL, WARNING, ADVISORY
    current_stock: int
    runway_days: float
    burn_rate: float
    recommended_action: str
    timestamp: str

class TransferRecommendation(BaseModel):
    id: str
    item_id: str
    item_name: str
    quantity: int
    unit: str
    source_facility_id: str
    source_facility_name: str
    source_district: str
    target_facility_id: str
    target_facility_name: str
    target_district: str
    distance_km: float
    estimated_transit_hours: float
    priority: str # EMERGENCY, HIGH, ROUTINE
    cold_chain_required: bool
    status: str = "PENDING_APPROVAL" # PENDING_APPROVAL, DISPATCHED, IN_TRANSIT, DELIVERED
    rationale: str
    created_at: str

class ForecastPoint(BaseModel):
    date: str
    predicted_demand: float
    lower_ci: float
    upper_ci: float

class ForecastResponse(BaseModel):
    item_id: str
    item_name: str
    facility_id: Optional[str] = "NATIONAL_AGGREGATE"
    facility_name: Optional[str] = "All PHC Network"
    historical_dates: List[str]
    historical_values: List[float]
    forecast_dates: List[str]
    forecast_values: List[float]
    lower_bounds: List[float]
    upper_bounds: List[float]
    confidence_score: float
    surge_index: float
    growth_rate_pct: float
    risk_assessment: str

class FederatedNodeStatus(BaseModel):
    id: str
    country: str
    flag: str
    role: str
    institution: str
    facilities_monitored: int
    status: str
    latency_ms: int
    federation_contribution: float
    last_sync: str
    privacy_budget_eps: float
    local_loss: float
    data_points: int

class FederatedRoundResponse(BaseModel):
    round_id: int
    timestamp: str
    participating_nodes: int
    global_model_loss: float
    loss_reduction_pct: float
    mean_absolute_error: float
    privacy_budget_spent: float
    differential_privacy_guarantee: str
    node_contributions: List[Dict[str, Any]]
    model_version: str

class SimulationTriggerRequest(BaseModel):
    scenario_id: str # dengue_surge, respiratory_wave, flood_disruption, brics_cross_border
    intensity: float = 1.0 # 0.5 to 2.0
    affected_district: Optional[str] = "ALL"

class SystemStats(BaseModel):
    total_facilities: int
    phc_count: int
    chc_count: int
    dh_count: int
    total_beds: int
    occupied_beds: int
    total_doctors_on_duty: int
    total_nurses_on_duty: int
    critical_stockouts_count: int
    warning_stockouts_count: int
    active_transfers_count: int
    federated_nodes_active: int
    overall_system_resilience_score: float # 0 to 100
