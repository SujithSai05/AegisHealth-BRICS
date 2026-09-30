"""
Database seeder with realistic Primary Health Centres (PHCs), CHCs, District Hospitals,
staffing, bed capacity, essential medicines inventory, and 90-day historical time-series data.
"""
import random
import datetime
from typing import List, Dict, Any
from aegis.config import MEDICINE_CATALOG

# Districts configuration with geospatial centerpoints
DISTRICTS = [
    {"name": "Krishna Delta", "state": "Andhra Pradesh", "lat": 16.5062, "lon": 80.6480, "type_bias": "flood_prone"},
    {"name": "Visakha Agency", "state": "Andhra Pradesh", "lat": 17.6868, "lon": 83.2185, "type_bias": "tribal_coastal"},
    {"name": "Chittoor Highlands", "state": "Andhra Pradesh", "lat": 13.2172, "lon": 79.1003, "type_bias": "rural_hills"},
    {"name": "Guntur Plains", "state": "Andhra Pradesh", "lat": 16.3067, "lon": 80.4365, "type_bias": "dense_agriculture"},
    {"name": "Kurnool Arid Zone", "state": "Andhra Pradesh", "lat": 15.8281, "lon": 78.0373, "type_bias": "semi_arid"},
    {"name": "Ranga Reddy Fringe", "state": "Telangana", "lat": 17.3850, "lon": 78.4867, "type_bias": "peri_urban"}
]

FACILITY_TEMPLATES = [
    # Krishna Delta
    {"name": "Avanigadda Primary Health Centre", "code": "PHC-KD-01", "type": "PHC", "dist": 0, "pop": 24000, "lat_off": 0.05, "lon_off": 0.08},
    {"name": "Machilipatnam Community Health Centre", "code": "CHC-KD-02", "type": "CHC", "dist": 0, "pop": 68000, "lat_off": -0.02, "lon_off": 0.12},
    {"name": "Gudivada Sub-District Hospital", "code": "SDH-KD-03", "type": "CHC", "dist": 0, "pop": 92000, "lat_off": 0.11, "lon_off": -0.04},
    {"name": "Vijayawada District General Hospital", "code": "DH-KD-04", "type": "DH", "dist": 0, "pop": 340000, "lat_off": 0.01, "lon_off": -0.02},

    # Visakha Agency
    {"name": "Paderu Tribal Primary Health Centre", "code": "PHC-VA-01", "type": "PHC", "dist": 1, "pop": 18500, "lat_off": 0.28, "lon_off": -0.32},
    {"name": "Araku Valley Community Health Centre", "code": "CHC-VA-02", "type": "CHC", "dist": 1, "pop": 54000, "lat_off": 0.42, "lon_off": -0.28},
    {"name": "Anakapalle Community Health Centre", "code": "CHC-VA-03", "type": "CHC", "dist": 1, "pop": 76000, "lat_off": -0.08, "lon_off": -0.19},
    {"name": "King George District Hospital Visakhapatnam", "code": "DH-VA-04", "type": "DH", "dist": 1, "pop": 420000, "lat_off": 0.02, "lon_off": 0.01},

    # Chittoor Highlands
    {"name": "Kuppam Border Primary Health Centre", "code": "PHC-CH-01", "type": "PHC", "dist": 2, "pop": 29000, "lat_off": -0.35, "lon_off": -0.18},
    {"name": "Punganur Community Health Centre", "code": "CHC-CH-02", "type": "CHC", "dist": 2, "pop": 61000, "lat_off": 0.12, "lon_off": -0.24},
    {"name": "Madanapalle Sub-District Hospital", "code": "SDH-CH-03", "type": "CHC", "dist": 2, "pop": 110000, "lat_off": 0.25, "lon_off": -0.38},
    {"name": "Chittoor District Headquarters Hospital", "code": "DH-CH-04", "type": "DH", "dist": 2, "pop": 280000, "lat_off": 0.01, "lon_off": 0.02},

    # Guntur Plains
    {"name": "Mangalagiri Primary Health Centre", "code": "PHC-GP-01", "type": "PHC", "dist": 3, "pop": 32000, "lat_off": 0.12, "lon_off": 0.09},
    {"name": "Tenali Community Health Centre", "code": "CHC-GP-02", "type": "CHC", "dist": 3, "pop": 85000, "lat_off": -0.08, "lon_off": 0.18},
    {"name": "Narasaraopet Community Hospital", "code": "CHC-GP-03", "type": "CHC", "dist": 3, "pop": 78000, "lat_off": -0.12, "lon_off": -0.32},
    {"name": "Guntur Comprehensive District Hospital", "code": "DH-GP-04", "type": "DH", "dist": 3, "pop": 390000, "lat_off": -0.01, "lon_off": 0.01},

    # Kurnool Arid Zone
    {"name": "Adoni Primary Health Centre", "code": "PHC-KZ-01", "type": "PHC", "dist": 4, "pop": 26000, "lat_off": -0.15, "lon_off": -0.58},
    {"name": "Nandyal Community Health Centre", "code": "CHC-KZ-02", "type": "CHC", "dist": 4, "pop": 72000, "lat_off": -0.32, "lon_off": 0.38},
    {"name": "Yemmiganur Rural Primary Health Centre", "code": "PHC-KZ-03", "type": "PHC", "dist": 4, "pop": 22000, "lat_off": -0.08, "lon_off": -0.42},
    {"name": "Kurnool Government General Hospital", "code": "DH-KZ-04", "type": "DH", "dist": 4, "pop": 360000, "lat_off": 0.02, "lon_off": -0.01},

    # Ranga Reddy Fringe
    {"name": "Shadnagar Primary Health Centre", "code": "PHC-RR-01", "type": "PHC", "dist": 5, "pop": 34000, "lat_off": -0.32, "lon_off": -0.22},
    {"name": "Ibrahimpatnam Community Health Centre", "code": "CHC-RR-02", "type": "CHC", "dist": 5, "pop": 64000, "lat_off": -0.21, "lon_off": 0.28},
    {"name": "Chevella Rural Primary Health Centre", "code": "PHC-RR-03", "type": "PHC", "dist": 5, "pop": 27000, "lat_off": 0.08, "lon_off": -0.35},
    {"name": "Hayathnagar Area Hospital", "code": "DH-RR-04", "type": "DH", "dist": 5, "pop": 290000, "lat_off": -0.12, "lon_off": 0.18}
]

def generate_seed_facilities() -> List[Dict[str, Any]]:
    """Generates the full list of facility objects with beds, staff, and inventory."""
    facilities = []
    random.seed(42) # Deterministic realistic seed

    for i, t in enumerate(FACILITY_TEMPLATES):
        dist_meta = DISTRICTS[t["dist"]]
        fac_type = t["type"]

        # Capacity scales by facility tier
        if fac_type == "PHC":
            total_beds = random.randint(6, 12)
            icu_total = 0
            oxygen_total = random.randint(2, 4)
            general_total = total_beds - oxygen_total
            isolation_total = random.randint(1, 2)
            doc_total = random.randint(2, 4)
            doc_duty = max(1, doc_total - random.randint(0, 1))
            nurse_total = random.randint(4, 8)
            nurse_duty = max(2, nurse_total - random.randint(0, 2))
            pharm_duty = random.randint(1, 2)
            lab_duty = random.randint(1, 2)
            asha_active = random.randint(12, 24)
            burn_factor = 1.0

        elif fac_type == "CHC":
            total_beds = random.randint(30, 60)
            icu_total = random.randint(4, 8)
            oxygen_total = random.randint(10, 20)
            general_total = total_beds - icu_total - oxygen_total
            isolation_total = random.randint(4, 8)
            doc_total = random.randint(8, 16)
            doc_duty = max(4, doc_total - random.randint(1, 3))
            nurse_total = random.randint(18, 32)
            nurse_duty = max(12, nurse_total - random.randint(2, 5))
            pharm_duty = random.randint(2, 4)
            lab_duty = random.randint(3, 6)
            asha_active = random.randint(40, 75)
            burn_factor = 3.5

        else: # District Hospital (DH)
            total_beds = random.randint(150, 300)
            icu_total = random.randint(20, 40)
            oxygen_total = random.randint(50, 90)
            general_total = total_beds - icu_total - oxygen_total
            isolation_total = random.randint(15, 30)
            doc_total = random.randint(35, 65)
            doc_duty = max(22, doc_total - random.randint(3, 8))
            nurse_total = random.randint(70, 130)
            nurse_duty = max(50, nurse_total - random.randint(5, 15))
            pharm_duty = random.randint(6, 12)
            lab_duty = random.randint(10, 22)
            asha_active = random.randint(120, 210)
            burn_factor = 12.0

        # Occupancy rates
        occ_ratio = random.uniform(0.55, 0.88)
        # Induce a critical surge in a couple of facilities for demonstration
        if i in [0, 4, 16]: # Avanigadda, Paderu, Adoni have acute strains
            occ_ratio = random.uniform(0.92, 0.98)

        occupied_beds = int(total_beds * occ_ratio)
        avail_beds = max(0, total_beds - occupied_beds)
        icu_occ = min(icu_total, int(icu_total * (occ_ratio + random.uniform(-0.05, 0.1))))
        oxy_occ = min(oxygen_total, int(oxygen_total * (occ_ratio + random.uniform(-0.05, 0.08))))
        gen_occ = min(general_total, int(general_total * occ_ratio))
        iso_occ = min(isolation_total, int(isolation_total * random.uniform(0.4, 0.9)))

        att_ratio = round((doc_duty + nurse_duty) / (doc_total + nurse_total), 2)
        staff_status = "NORMAL" if att_ratio >= 0.75 else ("STRESSED" if att_ratio >= 0.6 else "SEVERE")

        # Inventory generation
        inventory = []
        critical_count = 0
        warning_count = 0

        for med in MEDICINE_CATALOG:
            # Baseline daily consumption
            base_burn = round(random.uniform(8, 25) * burn_factor, 1)
            min_thresh = int(base_burn * med["min_default_buffer_days"])

            # Create specific realistic vulnerabilities
            # Avanigadda PHC (flood-prone): Normal Saline IV & ORS stockout crisis
            if i == 0 and med["id"] in ["MED-004", "MED-005"]:
                current_stock = int(base_burn * random.uniform(1.2, 2.4)) # only 1-2 days remaining!
            # Paderu Tribal PHC: Antivenom & ACT Antimalarial near zero
            elif i == 4 and med["id"] in ["MED-003", "MED-008"]:
                current_stock = int(base_burn * random.uniform(0.8, 2.0))
            # Adoni PHC: Amoxicillin & Azithromycin critical
            elif i == 16 and med["id"] in ["MED-001", "MED-002"]:
                current_stock = int(base_burn * random.uniform(1.0, 2.2))
            # District Hospitals typically have surplus reserves
            elif fac_type == "DH":
                current_stock = int(base_burn * random.uniform(26, 42)) # Surplus donor
            else:
                current_stock = int(base_burn * random.uniform(8, 30))

            days_runway = round(current_stock / max(0.1, base_burn), 1)

            if days_runway <= 3.0:
                item_status = "CRITICAL"
                critical_count += 1
            elif days_runway <= 7.0:
                item_status = "WARNING"
                warning_count += 1
            elif days_runway > 25.0:
                item_status = "SURPLUS"
            else:
                item_status = "OPTIMAL"

            today = datetime.date(2026, 9, 26)
            exp_days = random.randint(180, 720)
            exp_date = (today + datetime.timedelta(days=exp_days)).isoformat()
            batch_no = f"BAT-{med['id'][-3:]}-{random.randint(100, 999)}"

            inventory.append({
                "id": med["id"],
                "name": med["name"],
                "category": med["category"],
                "unit": med["unit"],
                "current_stock": current_stock,
                "min_threshold": min_thresh,
                "daily_burn_rate": base_burn,
                "days_runway": days_runway,
                "cold_chain": med["cold_chain"],
                "temp_range": med.get("temp_range", None),
                "batch_no": batch_no,
                "expiry_date": exp_date,
                "status": item_status
            })

        # Overall facility status & risk score
        risk_score = round(min(100.0, (critical_count * 32.0 + warning_count * 14.0 + (occ_ratio * 40.0) + (1.0 - att_ratio) * 30.0)), 1)
        if critical_count > 0 or occ_ratio > 0.92 or att_ratio < 0.60:
            overall_status = "CRITICAL"
        elif warning_count > 0 or occ_ratio > 0.78 or att_ratio < 0.72:
            overall_status = "WARNING"
        else:
            overall_status = "STABLE"

        facility = {
            "id": f"FAC-{i+1:03d}",
            "name": t["name"],
            "code": t["code"],
            "type": fac_type,
            "district": dist_meta["name"],
            "state": dist_meta["state"],
            "latitude": round(dist_meta["lat"] + t["lat_off"], 4),
            "longitude": round(dist_meta["lon"] + t["lon_off"], 4),
            "catchment_population": t["pop"],
            "beds": {
                "total": total_beds,
                "occupied": occupied_beds,
                "available": avail_beds,
                "icu_total": icu_total,
                "icu_occupied": icu_occ,
                "oxygen_total": oxygen_total,
                "oxygen_occupied": oxy_occ,
                "general_total": general_total,
                "general_occupied": gen_occ,
                "isolation_total": isolation_total,
                "isolation_occupied": iso_occ,
                "occupancy_rate": round(occupied_beds / max(1, total_beds), 2)
            },
            "staff": {
                "doctors_total": doc_total,
                "doctors_on_duty": doc_duty,
                "nurses_total": nurse_total,
                "nurses_on_duty": nurse_duty,
                "pharmacists_on_duty": pharm_duty,
                "lab_techs_on_duty": lab_duty,
                "asha_workers_active": asha_active,
                "attendance_ratio": att_ratio,
                "status": staff_status
            },
            "inventory": inventory,
            "overall_status": overall_status,
            "risk_score": risk_score,
            "last_reported": "2026-09-26T20:15:00Z"
        }
        facilities.append(facility)

    return facilities

def generate_historical_time_series(days: int = 90) -> Dict[str, Any]:
    """Generates 90 days of daily footfall, OPD visits, and medicine consumption for ML training."""
    random.seed(101)
    end_date = datetime.date(2026, 9, 26)
    start_date = end_date - datetime.timedelta(days=days - 1)

    dates = [(start_date + datetime.timedelta(days=d)).isoformat() for d in range(days)]

    # Generate synthetic patterns with weekday seasonality, monsoon surge, and syndromic indicators
    records = []
    for d_idx, dt_str in enumerate(dates):
        # Day of week effect (Mondays peak, Sundays dip)
        dow = (d_idx % 7)
        dow_mult = 1.35 if dow == 0 else (0.75 if dow == 6 else 1.0)

        # Monsoon seasonal wave (dengue/malaria/diarrhea rise between day 40 and 85)
        monsoon_wave = 1.0 + 0.45 * (1.0 if 40 <= d_idx <= 85 else 0.1)

        # Footfall base
        base_footfall = int((14500 + 400 * (d_idx / 90.0) + random.uniform(-600, 800)) * dow_mult * monsoon_wave)

        # Medicine consumption across all monitored facilities
        item_consumptions = {
            "MED-001": int((8200 + random.uniform(-400, 500)) * dow_mult * monsoon_wave),
            "MED-002": int((5400 + random.uniform(-300, 450)) * dow_mult * (1.0 + (0.3 if d_idx > 60 else 0.0))),
            "MED-003": int((3200 + random.uniform(-250, 300)) * monsoon_wave * 1.3),
            "MED-004": int((11200 + random.uniform(-700, 900)) * monsoon_wave * 1.25),
            "MED-005": int((9500 + random.uniform(-500, 700)) * monsoon_wave * 1.4),
            "MED-006": int(2100 + random.uniform(-100, 150)),
            "MED-007": int(1850 + random.uniform(-80, 120)),
            "MED-008": int((480 + random.uniform(-40, 60)) * (1.5 if 40 <= d_idx <= 85 else 1.0)),
            "MED-009": int((16500 + random.uniform(-900, 1200)) * dow_mult * monsoon_wave),
            "MED-010": int((1250 + random.uniform(-80, 120)) * (1.0 + (0.25 if d_idx > 65 else 0.0))),
            "MED-011": int((2900 + random.uniform(-150, 200)) * (1.4 if dow in [2, 4] else 0.8)), # immunization days
            "MED-012": int((3800 + random.uniform(-200, 300)) * monsoon_wave * 1.5)
        }

        records.append({
            "date": dt_str,
            "total_footfall": base_footfall,
            "opd_visits": int(base_footfall * 0.82),
            "ipd_admissions": int(base_footfall * 0.12),
            "emergency_triaged": int(base_footfall * 0.06),
            "syndromic_ari": int(base_footfall * 0.28),
            "syndromic_vector_borne": int(base_footfall * (0.22 if 40 <= d_idx <= 85 else 0.08)),
            "syndromic_diarrheal": int(base_footfall * (0.19 if 40 <= d_idx <= 85 else 0.11)),
            "medicine_consumption": item_consumptions
        })

    return {"dates": dates, "records": records}
