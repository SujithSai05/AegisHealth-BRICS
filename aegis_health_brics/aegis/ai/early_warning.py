"""
Early Warning and Stock-Out Triage Engine for AegisHealth BRICS.
Monitors inventory runways, bed stress, and medical staffing ratios.
"""
import datetime
from typing import List, Dict, Any
from aegis.database.db import db
from aegis.config import CRITICAL_RUNWAY_DAYS, WARNING_RUNWAY_DAYS

class EarlyWarningEngine:
    def evaluate_facility_risk(self, facility: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates a holistic vulnerability risk index for a given health facility.
        Factors:
        - Medicine Stockout Urgency (50%)
        - Bed Capacity Strain (30%)
        - Medical Staff Attendance Stress (20%)
        """
        inventory = facility["inventory"]
        beds = facility["beds"]
        staff = facility["staff"]

        # 1. Inventory stockout score
        crit_meds = [m for m in inventory if m["days_runway"] <= CRITICAL_RUNWAY_DAYS]
        warn_meds = [m for m in inventory if CRITICAL_RUNWAY_DAYS < m["days_runway"] <= WARNING_RUNWAY_DAYS]

        med_score = min(100.0, (len(crit_meds) * 35.0) + (len(warn_meds) * 15.0))

        # 2. Bed strain score
        occ_rate = beds.get("occupancy_rate", 0.0)
        icu_total = beds.get("icu_total", 0)
        icu_occ = beds.get("icu_occupied", 0)
        icu_rate = (icu_occ / icu_total) if icu_total > 0 else 0.0

        bed_score = min(100.0, (occ_rate * 50.0) + (icu_rate * 50.0))

        # 3. Staffing attendance score
        att_rate = staff.get("attendance_ratio", 1.0)
        staff_deficit = max(0.0, 1.0 - att_rate)
        staff_score = min(100.0, staff_deficit * 200.0)

        # Composite weighted risk index
        total_risk = round(0.50 * med_score + 0.30 * bed_score + 0.20 * staff_score, 1)

        if total_risk >= 70.0 or len(crit_meds) > 0 or icu_rate >= 0.95:
            threat_level = "CRITICAL"
        elif total_risk >= 40.0 or len(warn_meds) > 0 or occ_rate >= 0.80:
            threat_level = "WARNING"
        else:
            threat_level = "STABLE"

        return {
            "facility_id": facility["id"],
            "facility_name": facility["name"],
            "total_risk_score": total_risk,
            "threat_level": threat_level,
            "critical_medicines_count": len(crit_meds),
            "warning_medicines_count": len(warn_meds),
            "bed_occupancy_rate": occ_rate,
            "staff_attendance_rate": att_rate,
            "urgent_items": [{"id": m["id"], "name": m["name"], "runway": m["days_runway"]} for m in crit_meds]
        }

    def generate_system_alerts(self) -> List[Dict[str, Any]]:
        """Scans all facilities and generates actionable emergency alerts."""
        return db.get_alerts()

    def simulate_dispatch_notification(self, alert_id: str) -> Dict[str, Any]:
        """Simulates automated SMS / emergency push notification to district health officer."""
        alerts = db.get_alerts()
        target = next((a for a in alerts if a["id"] == alert_id), None)
        if not target:
            return {"status": "ERROR", "message": f"Alert {alert_id} not found."}

        return {
            "status": "DISPATCHED",
            "alert_id": alert_id,
            "recipient": f"District Health Officer ({target['district']}) & PHC In-charge ({target['facility_name']})",
            "channel": "National SMS Emergency Gateway & Aegis Mobile Triage Push",
            "message": f"[AEGIS-CRITICAL] Urgent stockout warning at {target['facility_name']}. Item: {target['item_name']}. Estimated runway: {target['runway_days']} days. Automated redistribution plan staged.",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# Global early warning engine instance
early_warning = EarlyWarningEngine()
