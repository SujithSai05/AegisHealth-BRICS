"""
Unit tests for Machine Learning Demand Forecaster & Early Warning.
"""
import unittest
from aegis.ai.forecaster import forecaster
from aegis.ai.early_warning import early_warning
from aegis.database.db import db

class TestForecasting(unittest.TestCase):
    def setUp(self):
        db.initialize()

    def test_forecast_demand_structure(self):
        # Forecast for Normal Saline IV (MED-004) over 14 days
        res = forecaster.forecast_demand("MED-004", horizon_days=14)
        self.assertEqual(res["item_id"], "MED-004")
        self.assertEqual(len(res["forecast_dates"]), 14)
        self.assertEqual(len(res["forecast_values"]), 14)
        self.assertEqual(len(res["lower_bounds"]), 14)
        self.assertEqual(len(res["upper_bounds"]), 14)

        # Upper bounds must be >= forecast values >= lower bounds
        for pred, low, up in zip(res["forecast_values"], res["lower_bounds"], res["upper_bounds"]):
            self.assertGreaterEqual(pred, low)
            self.assertGreaterEqual(up, pred)

    def test_early_warning_evaluation(self):
        facilities = db.get_facilities()
        self.assertGreater(len(facilities), 0)

        # Check facility risk evaluation
        fac = facilities[0]
        eval_res = early_warning.evaluate_facility_risk(fac)
        self.assertIn("total_risk_score", eval_res)
        self.assertIn("threat_level", eval_res)
        self.assertTrue(0.0 <= eval_res["total_risk_score"] <= 100.0)

    def test_sms_alert_dispatch(self):
        alerts = db.get_alerts()
        self.assertGreater(len(alerts), 0)
        first_alert = alerts[0]
        dispatch_res = early_warning.simulate_dispatch_notification(first_alert["id"])
        self.assertEqual(dispatch_res["status"], "DISPATCHED")
        self.assertEqual(dispatch_res["alert_id"], first_alert["id"])

if __name__ == "__main__":
    unittest.main()
