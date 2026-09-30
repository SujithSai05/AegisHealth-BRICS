"""
Unit tests for Cross-District Resource Redistribution Optimizer.
"""
import unittest
from aegis.ai.redistributor import redistributor, haversine_distance_km
from aegis.database.db import db

class TestRedistribution(unittest.TestCase):
    def setUp(self):
        db.initialize()

    def test_haversine_distance(self):
        # Distance between Vijayawada (16.5062, 80.6480) and Guntur (16.3067, 80.4365) ~ 31 km
        d = haversine_distance_km(16.5062, 80.6480, 16.3067, 80.4365)
        self.assertGreater(d, 20.0)
        self.assertLess(d, 45.0)

    def test_optimization_recommendations(self):
        recs = redistributor.optimize_redistribution()
        self.assertIsInstance(recs, list)
        self.assertGreater(len(recs), 0, "Should generate transfer recommendations for seeded low-runway facilities")

        for r in recs:
            self.assertIn("source_facility_id", r)
            self.assertIn("target_facility_id", r)
            self.assertNotEqual(r["source_facility_id"], r["target_facility_id"])
            self.assertGreater(r["quantity"], 0)
            self.assertGreater(r["distance_km"], 0.0)

    def test_auto_dispatch(self):
        recs = redistributor.optimize_redistribution()
        self.assertGreater(len(recs), 0)

        # Record target facility initial stock
        target_id = recs[0]["target_facility_id"]
        item_id = recs[0]["item_id"]
        target_fac = db.get_facility_by_id(target_id)
        init_stock = next(i["current_stock"] for i in target_fac["inventory"] if i["id"] == item_id)

        # Dispatch
        dispatched = redistributor.auto_dispatch_all([recs[0]])
        self.assertEqual(len(dispatched), 1)

        # Verify target facility stock increased
        updated_fac = db.get_facility_by_id(target_id)
        updated_stock = next(i["current_stock"] for i in updated_fac["inventory"] if i["id"] == item_id)
        self.assertGreater(updated_stock, init_stock)

if __name__ == "__main__":
    unittest.main()
