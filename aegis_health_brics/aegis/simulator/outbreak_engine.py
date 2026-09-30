"""
Crisis and Emergency Outbreak Simulation Engine for AegisHealth BRICS.
Allows health administrators to simulate real-world epidemiological and supply-chain stress tests.
"""
from typing import Dict, Any, Optional
from aegis.database.db import db
from aegis.config import CRITICAL_RUNWAY_DAYS, WARNING_RUNWAY_DAYS

SCENARIOS = {
    "dengue_surge": {
        "title": "Monsoon Dengue & Vector-Borne Surge",
        "description": "Heavy monsoon rains trigger acute vector breeding across Krishna Delta and Guntur Plains. Daily patient footfall surges by 180%, spiking demand for IV fluids, antipyretics, and rapid test kits.",
        "affected_commodities": ["MED-004", "MED-005", "MED-009", "MED-012"],
        "affected_districts": ["Krishna Delta", "Guntur Plains"],
        "burn_multiplier": 3.2,
        "bed_occupancy_boost": 0.25,
        "impact_summary": "IV Fluids (Normal Saline) and Paracetamol stock runways dropped to under 1.8 days in 6 PHCs. Bed occupancy escalated to 94%."
    },
    "respiratory_wave": {
        "title": "Novel Respiratory Infection Epidemic Wave",
        "description": "Winter atmospheric inversion and seasonal transmission trigger widespread acute respiratory infections. Severe cases requiring high-flow oxygen and ICU escalation rise sharply.",
        "affected_commodities": ["MED-002", "MED-010", "MED-001"],
        "affected_districts": ["Ranga Reddy Fringe", "Kurnool Arid Zone"],
        "burn_multiplier": 2.8,
        "bed_occupancy_boost": 0.30,
        "impact_summary": "Medical Oxygen Cylinders and Azithromycin critically depleted. ICU bed capacity at 96% in 4 facilities."
    },
    "flood_disruption": {
        "title": "Severe Coastal Flash Flood & Logistics Arterial Severance",
        "description": "A deep depression in the Bay of Bengal floods coastal highways, isolating rural PHCs and halting standard weekly delivery routes for 72 hours.",
        "affected_commodities": ["MED-001", "MED-004", "MED-006", "MED-007"],
        "affected_districts": ["Visakha Agency", "Krishna Delta"],
        "burn_multiplier": 1.5,
        "bed_occupancy_boost": 0.15,
        "impact_summary": "Local PHC stock runways falling towards zero without incoming re-supply. Cross-district emergency rerouting required."
    },
    "brics_cross_border": {
        "title": "BRICS Federated Early Warning: Cross-Hemisphere Viral Mutation Signal",
        "description": "Collaborative model updates from Brazil (Fiocruz) and South Africa (NICD) detect early genomic mutation signatures and transmission accelerations 3 weeks ahead of local detection.",
        "affected_commodities": ["MED-002", "MED-011", "MED-012"],
        "affected_districts": ["ALL"],
        "burn_multiplier": 1.6,
        "bed_occupancy_boost": 0.10,
        "impact_summary": "Federated AI updated local risk weights 18 days in advance, automatically staging preemptive buffer redistribution to avert stockouts."
    }
}

class OutbreakSimulator:
    def trigger_scenario(self, scenario_id: str, intensity: float = 1.0) -> Dict[str, Any]:
        """Applies scenario impact to the active database state."""
        if scenario_id == "reset":
            db.initialize()
            return {
                "scenario_id": "reset",
                "title": "System Reset",
                "status": "RESET_SUCCESS",
                "message": "All facilities, inventory buffers, and bed metrics restored to baseline status."
            }

        scenario = SCENARIOS.get(scenario_id)
        if not scenario:
            return {"error": f"Scenario {scenario_id} not recognized."}

        facilities = db.get_facilities()
        affected_count = 0

        target_districts = scenario["affected_districts"]
        target_meds = scenario["affected_commodities"]
        burn_mult = scenario["burn_multiplier"] * intensity
        bed_boost = scenario["bed_occupancy_boost"] * intensity

        for f in facilities:
            dist = f["district"]
            if "ALL" in target_districts or dist in target_districts:
                affected_count += 1
                # Increase burn rate and reduce stock on affected commodities
                for item in f["inventory"]:
                    if item["id"] in target_meds:
                        item["daily_burn_rate"] = round(item["daily_burn_rate"] * burn_mult, 1)
                        # Deplete stock realistically under sudden shock
                        item["current_stock"] = max(2, int(item["current_stock"] * 0.45))
                        item["days_runway"] = round(item["current_stock"] / max(0.1, item["daily_burn_rate"]), 1)
                        if item["days_runway"] <= CRITICAL_RUNWAY_DAYS:
                            item["status"] = "CRITICAL"
                        elif item["days_runway"] <= WARNING_RUNWAY_DAYS:
                            item["status"] = "WARNING"

                # Stress beds
                beds = f["beds"]
                new_occ = min(beds["total"], int(beds["occupied"] * (1.0 + bed_boost)))
                beds["occupied"] = new_occ
                beds["available"] = max(0, beds["total"] - new_occ)
                beds["occupancy_rate"] = round(new_occ / max(1, beds["total"]), 2)

                if beds["icu_total"] > 0:
                    beds["icu_occupied"] = min(beds["icu_total"], int(beds["icu_total"] * 0.95))
                if beds["oxygen_total"] > 0:
                    beds["oxygen_occupied"] = min(beds["oxygen_total"], int(beds["oxygen_total"] * 0.92))

        # Recompute facility risk scores and alerts
        db._recalculate_facility_risks()
        db.refresh_alerts()

        return {
            "scenario_id": scenario_id,
            "title": scenario["title"],
            "description": scenario["description"],
            "intensity": intensity,
            "affected_facilities": affected_count,
            "impact_summary": scenario["impact_summary"],
            "status": "ACTIVE_SIMULATION",
            "active_alerts_count": len(db.get_alerts())
        }

# Global outbreak simulator instance
outbreak_engine = OutbreakSimulator()
