"""
Configuration and constants for AegisHealth BRICS Resilience Platform.
"""
from typing import Dict, List, Any

# Platform Metadata
PLATFORM_NAME = "AegisHealth BRICS"
VERSION = "1.0.0"
THEME = "Smart Health & Supply Chain Resilience"
TRACK = "Track 3 - Code for Communities"

# Thresholds for early warning and triage
CRITICAL_RUNWAY_DAYS = 3.0    # Less than 3 days of supply remaining -> Urgent emergency
WARNING_RUNWAY_DAYS = 7.0     # 3 to 7 days of supply remaining -> Warning stage
OPTIMAL_RUNWAY_DAYS = 21.0    # 7 to 21 days -> Normal operating capacity
SURPLUS_RUNWAY_DAYS = 28.0    # Greater than 28 days -> Potential donor for redistribution

# Bed occupancy thresholds
BED_CRITICAL_OCCUPANCY = 0.90 # 90% occupancy triggers alert
BED_WARNING_OCCUPANCY = 0.75  # 75% occupancy triggers advisory

# Staffing threshold
MIN_STAFF_ATTENDANCE_RATIO = 0.70 # Under 70% attendance triggers staffing warning

# BRICS Alliance Member Nodes for Federated AI
BRICS_NODES: List[Dict[str, Any]] = [
    {
        "id": "IN-ICMR-01",
        "country": "India",
        "flag": "🇮🇳",
        "role": "Lead Hub & Primary Testbed",
        "institution": "National Health Mission & ICMR",
        "facilities_monitored": 28450,
        "status": "ONLINE",
        "latency_ms": 12,
        "federation_contribution": 38.5,
        "last_sync": "Just now",
        "privacy_budget_eps": 1.2
    },
    {
        "id": "BR-FIOCRUZ-01",
        "country": "Brazil",
        "flag": "🇧🇷",
        "role": "South American Node",
        "institution": "Fiocruz & SUS Health Surveillance",
        "facilities_monitored": 14200,
        "status": "ONLINE",
        "latency_ms": 128,
        "federation_contribution": 21.0,
        "last_sync": "1 min ago",
        "privacy_budget_eps": 1.1
    },
    {
        "id": "ZA-NDOH-01",
        "country": "South Africa",
        "flag": "🇿🇦",
        "role": "African Regional Hub",
        "institution": "National Dept of Health & NICD",
        "facilities_monitored": 8940,
        "status": "ONLINE",
        "latency_ms": 145,
        "federation_contribution": 14.8,
        "last_sync": "3 mins ago",
        "privacy_budget_eps": 1.4
    },
    {
        "id": "RU-ROSPOT-01",
        "country": "Russia",
        "flag": "🇷🇺",
        "role": "Eurasian Surveillance Node",
        "institution": "Rospotrebnadzor & Federal Health Agency",
        "facilities_monitored": 11300,
        "status": "ONLINE",
        "latency_ms": 112,
        "federation_contribution": 13.2,
        "last_sync": "2 mins ago",
        "privacy_budget_eps": 1.0
    },
    {
        "id": "CN-CDC-01",
        "country": "China",
        "flag": "🇨🇳",
        "role": "East Asian Logistics Node",
        "institution": "China CDC Health Supply Network",
        "facilities_monitored": 32100,
        "status": "ONLINE",
        "latency_ms": 86,
        "federation_contribution": 31.4,
        "last_sync": "Just now",
        "privacy_budget_eps": 0.95
    },
    {
        "id": "EG-UHIA-01",
        "country": "Egypt",
        "flag": "🇪🇬",
        "role": "North African Node",
        "institution": "Universal Health Insurance Authority",
        "facilities_monitored": 5400,
        "status": "ONLINE",
        "latency_ms": 135,
        "federation_contribution": 8.2,
        "last_sync": "4 mins ago",
        "privacy_budget_eps": 1.3
    }
]

# Essential Medicines Catalog
MEDICINE_CATALOG = [
    {
        "id": "MED-001",
        "name": "Amoxicillin + Clavulanic Acid 625mg",
        "category": "Antibiotic (Broad Spectrum)",
        "unit": "tablets",
        "cold_chain": False,
        "min_default_buffer_days": 14,
        "critical_emergency": True
    },
    {
        "id": "MED-002",
        "name": "Azithromycin 500mg",
        "category": "Respiratory Antibiotic",
        "unit": "tablets",
        "cold_chain": False,
        "min_default_buffer_days": 14,
        "critical_emergency": True
    },
    {
        "id": "MED-003",
        "name": "Artemether + Lumefantrine (ACT)",
        "category": "Antimalarial",
        "unit": "courses",
        "cold_chain": False,
        "min_default_buffer_days": 21,
        "critical_emergency": True
    },
    {
        "id": "MED-004",
        "name": "Normal Saline (0.9% NaCl) 500ml",
        "category": "Critical IV Fluid",
        "unit": "bottles",
        "cold_chain": False,
        "min_default_buffer_days": 10,
        "critical_emergency": True
    },
    {
        "id": "MED-005",
        "name": "Oral Rehydration Salts (ORS) WHO Formula",
        "category": "Electrolyte Solution",
        "unit": "sachets",
        "cold_chain": False,
        "min_default_buffer_days": 15,
        "critical_emergency": False
    },
    {
        "id": "MED-006",
        "name": "Insulin Glargine 100 IU/ml",
        "category": "Endocrine / Diabetes",
        "unit": "vials",
        "cold_chain": True,
        "temp_range": "2°C - 8°C",
        "min_default_buffer_days": 20,
        "critical_emergency": True
    },
    {
        "id": "MED-007",
        "name": "Oxytocin Injection 10 IU/ml",
        "category": "Maternal Health (PPH Prevention)",
        "unit": "ampoules",
        "cold_chain": True,
        "temp_range": "2°C - 8°C",
        "min_default_buffer_days": 18,
        "critical_emergency": True
    },
    {
        "id": "MED-008",
        "name": "Polyvalent Snake Antivenom 10ml",
        "category": "Emergency Antidote",
        "unit": "vials",
        "cold_chain": True,
        "temp_range": "2°C - 8°C",
        "min_default_buffer_days": 30,
        "critical_emergency": True
    },
    {
        "id": "MED-009",
        "name": "Paracetamol 500mg Tablets",
        "category": "Analgesic / Antipyretic",
        "unit": "tablets",
        "cold_chain": False,
        "min_default_buffer_days": 10,
        "critical_emergency": False
    },
    {
        "id": "MED-010",
        "name": "Medical Oxygen Cylinders (47L Type D)",
        "category": "Respiratory Life Support",
        "unit": "cylinders",
        "cold_chain": False,
        "min_default_buffer_days": 7,
        "critical_emergency": True
    },
    {
        "id": "MED-011",
        "name": "Pentavalent Vaccine (DTP-HepB-Hib)",
        "category": "Pediatric Immunization",
        "unit": "doses",
        "cold_chain": True,
        "temp_range": "2°C - 8°C",
        "min_default_buffer_days": 25,
        "critical_emergency": True
    },
    {
        "id": "MED-012",
        "name": "Rapid Diagnostic Test (RDT) Kits - Dengue & Malaria",
        "category": "Diagnostic Surveillance",
        "unit": "test kits",
        "cold_chain": False,
        "min_default_buffer_days": 14,
        "critical_emergency": True
    }
]
