import unittest

from tests.set_path import *
from tests.artifacts import TradeClient, MiningClient
from base_astro_bot.trade import TradeAssistant
from base_astro_bot.trade.data_structure import DataStructure


class TradeTests(unittest.TestCase):
    def setUp(self):
        self.trade = TradeAssistant(log_file=None, trade_data_client=TradeClient, mining_data_client=MiningClient)

    def test_trade_structure(self):
        self.assertIsInstance(self.trade.celestial_bodies, DataStructure)
        self.assertIsInstance(self.trade.locations, DataStructure)
        self.assertIsInstance(self.trade.commodities, DataStructure)
        self.assertIsInstance(self.trade.commodity_prices, DataStructure)
        self.assertIsInstance(self.trade.resources, DataStructure)
        self.assertIsInstance(self.trade.resource_prices, DataStructure)

    def test_route(self):
        routes = self.trade.get_trade_routes()
        self.assertIsInstance(routes, list)
        for route in routes:
            self.assertEqual(route[1][0][0], 'invested money')

    def test_mining(self):
        prices = self.trade.get_mining_prices()
        self.assertIsInstance(prices, list)
        for price in prices:
            self.assertIsInstance(price, dict)
            self.assertIn("Resource", price.keys())
            self.assertIn("Locations", price.keys())

        prices = self.trade.get_mining_prices('laranite')
        self.assertIsInstance(prices, list)
        for price in prices:
            self.assertIsInstance(price, dict)
            self.assertIn("aUEC/unit", price.keys())
            self.assertIn("Locations", price.keys())
            self.assertIn(28.436869253195784, price.values())
            self.assertIn("Levski @ Delamar", price.values())
