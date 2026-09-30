"""
API Route functional tests for AegisHealth BRICS.
Tests endpoint handler logic directly without external network dependencies.
"""
import unittest
from aegis.api.routes import (
    get_system_stats, get_facilities, get_facility_detail,
    get_alerts, dispatch_alert_notification, get_demand_forecast,
    get_redistribution_recommendations, dispatch_transfer,
    get_transfers, get_federated_nodes, get_federated_metrics,
    run_federated_round, trigger_simulation, get_medicine_catalog
)
from aegis.models.schemas import SimulationTriggerRequest
from aegis.database.db import db

class TestAPIRoutes(unittest.TestCase):
    def setUp(self):
        db.initialize()

    def test_get_stats(self):
        stats = get_system_stats()
        self.assertIn("total_facilities", stats)
        self.assertEqual(stats["total_facilities"], 24)
        self.assertGreater(stats["total_beds"], 0)
        self.assertIn("overall_system_resilience_score", stats)

    def test_get_facilities_and_filter(self):
        all_facs = get_facilities()
        self.assertEqual(len(all_facs), 24)

        # Test district filter
        kd_facs = get_facilities(district="Krishna Delta")
        self.assertEqual(len(kd_facs), 4)

        # Test type filter
        phc_facs = get_facilities(fac_type="PHC")
        self.assertGreater(len(phc_facs), 0)

    def test_get_facility_detail(self):
        fac = get_facility_detail("FAC-001")
        self.assertEqual(fac["id"], "FAC-001")
        self.assertIn("beds", fac)
        self.assertIn("staff", fac)
        self.assertIn("inventory", fac)

    def test_get_alerts_and_notify(self):
        alerts = get_alerts()
        self.assertIsInstance(alerts, list)
        if len(alerts) > 0:
            res = dispatch_alert_notification(alerts[0]["id"])
            self.assertEqual(res["status"], "DISPATCHED")

    def test_get_demand_forecast(self):
        fc = get_demand_forecast(item_id="MED-004", horizon_days=14)
        self.assertEqual(fc["item_id"], "MED-004")
        self.assertEqual(len(fc["forecast_dates"]), 14)
        self.assertIn("growth_rate_pct", fc)

    def test_redistribution_recommendations_and_dispatch(self):
        recs = get_redistribution_recommendations()
        self.assertGreater(len(recs), 0)

        dispatch_res = dispatch_transfer(auto_all=True)
        self.assertEqual(dispatch_res["status"], "SUCCESS")
        self.assertGreater(dispatch_res["dispatched_count"], 0)

        transfers = get_transfers()
        self.assertGreater(len(transfers), 0)

    def test_federated_routes(self):
        nodes = get_federated_nodes()
        self.assertGreaterEqual(len(nodes), 6)

        metrics = get_federated_metrics()
        self.assertIn("rounds_history", metrics)

        round_res = run_federated_round()
        self.assertIn("round_id", round_res)

    def test_simulation_trigger_and_reset(self):
        # Trigger Dengue surge
        req = SimulationTriggerRequest(scenario_id="dengue_surge", intensity=1.0)
        sim_res = trigger_simulation(req)
        self.assertEqual(sim_res["status"], "ACTIVE_SIMULATION")

        # Reset
        req_reset = SimulationTriggerRequest(scenario_id="reset")
        reset_res = trigger_simulation(req_reset)
        self.assertEqual(reset_res["status"], "RESET_SUCCESS")

    def test_catalog(self):
        catalog = get_medicine_catalog()
        self.assertEqual(len(catalog), 12)

if __name__ == "__main__":
    unittest.main()
