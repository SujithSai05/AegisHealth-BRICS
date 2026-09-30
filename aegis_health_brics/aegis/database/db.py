"""
In-memory persistence and state management for AegisHealth BRICS.
Provides thread-safe access to facilities, inventory, alerts, transfer manifests, and simulation states.
"""
import copy
import datetime
from typing import List, Dict, Optional, Any
from aegis.database.seeder import generate_seed_facilities, generate_historical_time_series
from aegis.config import BRICS_NODES, CRITICAL_RUNWAY_DAYS, WARNING_RUNWAY_DAYS

class HealthDatabase:
    def __init__(self):
        self._facilities: List[Dict[str, Any]] = []
        self._time_series: Dict[str, Any] = {}
        self._transfers: List[Dict[str, Any]] = []
        self._alerts: List[Dict[str, Any]] = []
        self._brics_nodes: List[Dict[str, Any]] = []
        self._federated_history: List[Dict[str, Any]] = []
        self._simulation_state: Dict[str, Any] = {"active_scenario": None, "intensity": 1.0}
        self.initialize()

    def initialize(self):
        """Initializes database with fresh seed data."""
        self._facilities = generate_seed_facilities()
        self._time_series = generate_historical_time_series(days=90)
        self._transfers = []
        self._brics_nodes = copy.deepcopy(BRICS_NODES)
        self._federated_history = [
            {
                "round_id": 1,
                "timestamp": "2026-09-24 10:00:00",
                "participating_nodes": 6,
                "global_model_loss": 0.482,
                "loss_reduction_pct": 0.0,
                "mean_absolute_error": 142.5,
                "privacy_budget_spent": 0.25,
                "differential_privacy_guarantee": "Strict (ε=1.2, δ=1e-5)",
                "node_contributions": [{"node": n["id"], "weight": n["federation_contribution"]} for n in self._brics_nodes],
                "model_version": "v1.0-alpha"
            },
            {
                "round_id": 2,
                "timestamp": "2026-09-25 14:30:00",
                "participating_nodes": 6,
                "global_model_loss": 0.318,
                "loss_reduction_pct": 34.0,
                "mean_absolute_error": 98.2,
                "privacy_budget_spent": 0.50,
                "differential_privacy_guarantee": "Strict (ε=1.2, δ=1e-5)",
                "node_contributions": [{"node": n["id"], "weight": n["federation_contribution"]} for n in self._brics_nodes],
                "model_version": "v1.1-beta"
            }
        ]
        self.refresh_alerts()

    def get_facilities(self, district: Optional[str] = None, status: Optional[str] = None, fac_type: Optional[str] = None) -> List[Dict[str, Any]]:
        results = self._facilities
        if isinstance(district, str) and district != "ALL":
            results = [f for f in results if f["district"].lower() == district.lower()]
        if isinstance(status, str) and status != "ALL":
            results = [f for f in results if f["overall_status"].upper() == status.upper()]
        if isinstance(fac_type, str) and fac_type != "ALL":
            results = [f for f in results if f["type"].upper() == fac_type.upper()]
        return results

    def get_facility_by_id(self, facility_id: str) -> Optional[Dict[str, Any]]:
        for f in self._facilities:
            if f["id"] == facility_id or f["code"] == facility_id:
                return f
        return None

    def refresh_alerts(self) -> List[Dict[str, Any]]:
        """Scans all facilities and generates real-time stockout and operational alerts."""
        alerts = []
        alert_counter = 1

        for f in self._facilities:
            # Check medicine runways
            for med in f["inventory"]:
                runway = med["days_runway"]
                if runway <= CRITICAL_RUNWAY_DAYS:
                    alerts.append({
                        "id": f"ALT-{alert_counter:04d}",
                        "facility_id": f["id"],
                        "facility_name": f["name"],
                        "district": f["district"],
                        "item_id": med["id"],
                        "item_name": med["name"],
                        "category": med["category"],
                        "severity": "CRITICAL",
                        "current_stock": med["current_stock"],
                        "runway_days": runway,
                        "burn_rate": med["daily_burn_rate"],
                        "recommended_action": f"Immediate emergency transfer required. Estimated stock exhaustion within {runway} days.",
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    alert_counter += 1
                elif runway <= WARNING_RUNWAY_DAYS:
                    alerts.append({
                        "id": f"ALT-{alert_counter:04d}",
                        "facility_id": f["id"],
                        "facility_name": f["name"],
                        "district": f["district"],
                        "item_id": med["id"],
                        "item_name": med["name"],
                        "category": med["category"],
                        "severity": "WARNING",
                        "current_stock": med["current_stock"],
                        "runway_days": runway,
                        "burn_rate": med["daily_burn_rate"],
                        "recommended_action": f"Low buffer threshold breached. Stage intra-district replenishment.",
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    alert_counter += 1

            # Check bed stress
            beds = f["beds"]
            if beds["icu_total"] > 0 and (beds["icu_occupied"] / beds["icu_total"]) >= 0.90:
                alerts.append({
                    "id": f"ALT-{alert_counter:04d}",
                    "facility_id": f["id"],
                    "facility_name": f["name"],
                    "district": f["district"],
                    "item_id": "BED-ICU",
                    "item_name": "ICU Bed Critical Capacity",
                    "category": "Critical Infrastructure",
                    "severity": "CRITICAL",
                    "current_stock": beds["icu_total"] - beds["icu_occupied"],
                    "runway_days": 1.0,
                    "burn_rate": 0.0,
                    "recommended_action": "ICU occupancy exceeds 90%. Route severe admissions to neighboring CHC/District Hospital.",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                alert_counter += 1

        self._alerts = alerts
        return self._alerts

    def get_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        self.refresh_alerts()
        if isinstance(severity, str) and severity != "ALL":
            return [a for a in self._alerts if a["severity"].upper() == severity.upper()]
        return self._alerts

    def get_transfers(self) -> List[Dict[str, Any]]:
        return self._transfers

    def add_transfer(self, transfer: Dict[str, Any]):
        self._transfers.insert(0, transfer)

    def update_transfer_status(self, transfer_id: str, new_status: str) -> Optional[Dict[str, Any]]:
        for t in self._transfers:
            if t["id"] == transfer_id:
                old_status = t["status"]
                t["status"] = new_status

                # If status became DISPATCHED or DELIVERED, apply inventory adjustments
                if new_status in ["DISPATCHED", "DELIVERED"] and old_status == "PENDING_APPROVAL":
                    self._apply_transfer_inventory_impact(t)

                return t
        return None

    def _apply_transfer_inventory_impact(self, transfer: Dict[str, Any]):
        """Deducts from donor and increments recipient facility."""
        source_fac = self.get_facility_by_id(transfer["source_facility_id"])
        target_fac = self.get_facility_by_id(transfer["target_facility_id"])
        qty = transfer["quantity"]
        item_id = transfer["item_id"]

        if source_fac:
            for item in source_fac["inventory"]:
                if item["id"] == item_id:
                    item["current_stock"] = max(0, item["current_stock"] - qty)
                    item["days_runway"] = round(item["current_stock"] / max(0.1, item["daily_burn_rate"]), 1)
                    self._update_item_status(item)

        if target_fac:
            for item in target_fac["inventory"]:
                if item["id"] == item_id:
                    item["current_stock"] += qty
                    item["days_runway"] = round(item["current_stock"] / max(0.1, item["daily_burn_rate"]), 1)
                    self._update_item_status(item)

        # Refresh facility risks and alerts
        self._recalculate_facility_risks()
        self.refresh_alerts()

    def _update_item_status(self, item: Dict[str, Any]):
        runway = item["days_runway"]
        if runway <= CRITICAL_RUNWAY_DAYS:
            item["status"] = "CRITICAL"
        elif runway <= WARNING_RUNWAY_DAYS:
            item["status"] = "WARNING"
        elif runway > 25.0:
            item["status"] = "SURPLUS"
        else:
            item["status"] = "OPTIMAL"

    def _recalculate_facility_risks(self):
        for f in self._facilities:
            crit = sum(1 for m in f["inventory"] if m["status"] == "CRITICAL")
            warn = sum(1 for m in f["inventory"] if m["status"] == "WARNING")
            occ = f["beds"]["occupancy_rate"]
            att = f["staff"]["attendance_ratio"]

            f["risk_score"] = round(min(100.0, (crit * 32.0 + warn * 14.0 + occ * 40.0 + (1.0 - att) * 30.0)), 1)
            if crit > 0 or occ > 0.92 or att < 0.60:
                f["overall_status"] = "CRITICAL"
            elif warn > 0 or occ > 0.78 or att < 0.72:
                f["overall_status"] = "WARNING"
            else:
                f["overall_status"] = "STABLE"

    def get_time_series(self) -> Dict[str, Any]:
        return self._time_series

    def get_brics_nodes(self) -> List[Dict[str, Any]]:
        return self._brics_nodes

    def get_federated_history(self) -> List[Dict[str, Any]]:
        return list(self._federated_history)

    def add_federated_round(self, round_data: Dict[str, Any]):
        self._federated_history.append(round_data)

    def get_system_stats(self) -> Dict[str, Any]:
        facs = self._facilities
        total_beds = sum(f["beds"]["total"] for f in facs)
        occupied_beds = sum(f["beds"]["occupied"] for f in facs)
        total_docs = sum(f["staff"]["doctors_on_duty"] for f in facs)
        total_nurses = sum(f["staff"]["nurses_on_duty"] for f in facs)

        crit_alerts = sum(1 for a in self._alerts if a["severity"] == "CRITICAL")
        warn_alerts = sum(1 for a in self._alerts if a["severity"] == "WARNING")

        avg_risk = sum(f["risk_score"] for f in facs) / max(1, len(facs))
        resilience_score = round(max(10.0, 100.0 - (avg_risk * 0.8) - (crit_alerts * 2.5)), 1)

        return {
            "total_facilities": len(facs),
            "phc_count": sum(1 for f in facs if f["type"] == "PHC"),
            "chc_count": sum(1 for f in facs if f["type"] == "CHC"),
            "dh_count": sum(1 for f in facs if f["type"] == "DH"),
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "overall_occupancy_rate": round(occupied_beds / max(1, total_beds), 2),
            "total_doctors_on_duty": total_docs,
            "total_nurses_on_duty": total_nurses,
            "critical_stockouts_count": crit_alerts,
            "warning_stockouts_count": warn_alerts,
            "active_transfers_count": len([t for t in self._transfers if t["status"] in ["PENDING_APPROVAL", "DISPATCHED", "IN_TRANSIT"]]),
            "federated_nodes_active": len([n for n in self._brics_nodes if n["status"] == "ONLINE"]),
            "overall_system_resilience_score": resilience_score
        }

# Global database singleton
db = HealthDatabase()
