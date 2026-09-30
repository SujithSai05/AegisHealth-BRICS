"""
Unit tests for BRICS Federated Learning Engine.
"""
import unittest
from aegis.ai.federated import federated_server
from aegis.database.db import db

class TestFederatedLearning(unittest.TestCase):
    def setUp(self):
        db.initialize()

    def test_alliance_nodes_active(self):
        nodes = federated_server.get_alliance_nodes()
        self.assertGreaterEqual(len(nodes), 6)
        countries = [n["country"] for n in nodes]
        self.assertIn("India", countries)
        self.assertIn("Brazil", countries)
        self.assertIn("South Africa", countries)

    def test_run_federated_round(self):
        metrics_before = federated_server.get_federated_metrics()
        initial_round = metrics_before["current_round"]

        round_res = federated_server.run_federated_round()
        self.assertEqual(round_res["round_id"], initial_round + 1)
        self.assertGreater(round_res["participating_nodes"], 0)
        self.assertIn("global_model_loss", round_res)
        self.assertIn("privacy_budget_spent", round_res)

        metrics_after = federated_server.get_federated_metrics()
        self.assertEqual(metrics_after["current_round"], initial_round + 1)
        self.assertGreater(len(metrics_after["rounds_history"]), len(metrics_before["rounds_history"]))

if __name__ == "__main__":
    unittest.main()
