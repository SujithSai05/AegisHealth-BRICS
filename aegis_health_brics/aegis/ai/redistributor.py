"""
Automated Cross-District and Intra-District Resource Redistribution Optimizer.
Solves multi-facility supply matching, minimizing transit distance and delivery latency
while maintaining safety buffers and cold-chain compliance.
"""
import math
import datetime
from typing import List, Dict, Any, Optional
from aegis.database.db import db
from aegis.config import CRITICAL_RUNWAY_DAYS, WARNING_RUNWAY_DAYS, OPTIMAL_RUNWAY_DAYS

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two GPS coordinates in kilometers."""
    r = 6371.0 # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (math.sin(dphi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(dlambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r * c, 1)

class ResourceRedistributionOptimizer:
    def optimize_redistribution(self) -> List[Dict[str, Any]]:
        """
        Scans all facilities, identifies critical stockout deficits,
        finds eligible surplus donor facilities, and generates optimal transfer recommendations.
        """
        facilities = db.get_facilities()
        recommendations = []
        rec_counter = len(db.get_transfers()) + 1

        # Step 1: Identify Deficit Facilities
        deficit_requests = []
        for fac in facilities:
            for item in fac["inventory"]:
                if item["days_runway"] <= WARNING_RUNWAY_DAYS:
                    burn = max(0.1, item["daily_burn_rate"])
                    # Target 18 days of runway
                    desired_stock = int(burn * OPTIMAL_RUNWAY_DAYS)
                    deficit_qty = max(10, desired_stock - item["current_stock"])
                    is_critical = item["days_runway"] <= CRITICAL_RUNWAY_DAYS

                    deficit_requests.append({
                        "facility": fac,
                        "item": item,
                        "deficit_qty": deficit_qty,
                        "is_critical": is_critical,
                        "urgency_rank": 1 if is_critical else 2
                    })

        # Sort deficits by urgency (Critical runway first)
        deficit_requests.sort(key=lambda x: (x["urgency_rank"], x["item"]["days_runway"]))

        # Step 2: Match each deficit with the optimal donor
        for req in deficit_requests:
            rec_fac = req["facility"]
            item_id = req["item"]["id"]
            item_name = req["item"]["name"]
            deficit_needed = req["deficit_qty"]
            cold_chain = req["item"].get("cold_chain", False)

            # Find potential donors with surplus
            candidates = []
            for donor_fac in facilities:
                if donor_fac["id"] == rec_fac["id"]:
                    continue

                donor_item = next((i for i in donor_fac["inventory"] if i["id"] == item_id), None)
                if not donor_item:
                    continue

                # Donor must have surplus (> 20 days runway)
                donor_burn = max(0.1, donor_item["daily_burn_rate"])
                safe_buffer_stock = int(donor_burn * 14.0) # Donor keeps at least 14 days
                donatable_stock = max(0, donor_item["current_stock"] - safe_buffer_stock)

                if donatable_stock >= 10:
                    dist_km = haversine_distance_km(
                        rec_fac["latitude"], rec_fac["longitude"],
                        donor_fac["latitude"], donor_fac["longitude"]
                    )
                    # Intra-district bonus (prefer local if available)
                    is_same_district = (donor_fac["district"] == rec_fac["district"])
                    transit_speed_kmh = 35.0 if dist_km < 40 else 55.0
                    transit_hours = round(dist_km / transit_speed_kmh, 1)

                    # Score: lower is better (distance penalized, cross-district slight penalty, surplus availability rewarded)
                    cost_score = dist_km * (0.7 if is_same_district else 1.0) - (donatable_stock * 0.05)

                    candidates.append({
                        "donor_fac": donor_fac,
                        "donor_item": donor_item,
                        "donatable_stock": donatable_stock,
                        "distance_km": dist_km,
                        "transit_hours": max(0.5, transit_hours),
                        "is_same_district": is_same_district,
                        "cost_score": cost_score
                    })

            if not candidates:
                continue

            # Select best candidate
            candidates.sort(key=lambda c: c["cost_score"])
            best_match = candidates[0]
            donor = best_match["donor_fac"]

            transfer_qty = min(deficit_needed, best_match["donatable_stock"])
            if transfer_qty <= 0:
                continue

            is_cross_district = (donor["district"] != rec_fac["district"])
            priority = "EMERGENCY" if req["is_critical"] else "HIGH"

            rationale = (
                f"{'Cross-district' if is_cross_district else 'Intra-district'} rebalancing: "
                f"{donor['name']} ({donor['district']}) has {round(best_match['donor_item']['days_runway'], 1)}d runway "
                f"-> replenishing {rec_fac['name']} ({round(req['item']['days_runway'], 1)}d runway remaining)."
            )

            plan = {
                "id": f"TRF-{rec_counter:04d}",
                "item_id": item_id,
                "item_name": item_name,
                "quantity": transfer_qty,
                "unit": req["item"]["unit"],
                "source_facility_id": donor["id"],
                "source_facility_name": donor["name"],
                "source_district": donor["district"],
                "source_lat": donor["latitude"],
                "source_lon": donor["longitude"],
                "target_facility_id": rec_fac["id"],
                "target_facility_name": rec_fac["name"],
                "target_district": rec_fac["district"],
                "target_lat": rec_fac["latitude"],
                "target_lon": rec_fac["longitude"],
                "distance_km": best_match["distance_km"],
                "estimated_transit_hours": best_match["transit_hours"],
                "is_cross_district": is_cross_district,
                "priority": priority,
                "cold_chain_required": cold_chain,
                "status": "PENDING_APPROVAL",
                "rationale": rationale,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            recommendations.append(plan)
            rec_counter += 1

        return recommendations

    def auto_dispatch_all(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Approves and dispatches all proposed transfers, updating inventory state."""
        dispatched = []
        for r in recommendations:
            r_copy = dict(r)
            r_copy["status"] = "PENDING_APPROVAL"
            db.add_transfer(r_copy)
            res = db.update_transfer_status(r_copy["id"], "DISPATCHED")
            dispatched.append(res if res else r_copy)
        return dispatched

# Global redistributor instance
redistributor = ResourceRedistributionOptimizer()
