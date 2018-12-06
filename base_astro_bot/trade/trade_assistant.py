from pymongo import MongoClient

from base_astro_bot.utils import MyLogger
from base_astro_bot.trade.data_structure import DataStructure
from base_astro_bot.trade.data_rat_client import TradeClient, MiningClient


class PricesStructure:

    def __init__(self, log_file="trade_assistant.log", mongo_client=None,
                 trade_data_client=TradeClient, mining_data_client=MiningClient):
        self._log_file = log_file
        self.logger = MyLogger(log_file_name=self._log_file, logger_name="Trade Assistant logger", prefix="[TRADE]")
        self.trade_data_client = trade_data_client()
        self.mining_data_client = mining_data_client()
        self.mongo_db = mongo_client   # type: MongoClient
        self.celestial_bodies = None   # type: DataStructure
        self.locations = None   # type: DataStructure
        self.commodities = None   # type: DataStructure
        self.commodity_prices = None   # type: DataStructure
        self.resources = None   # type: DataStructure
        self.resource_prices = None   # type: DataStructure
        self.update_data()

    def _update_data_structure(self):
        self.celestial_bodies = DataStructure(self.trade_data_client.get_containers())
        self.locations = DataStructure(self.trade_data_client.get_locations(), parents=self.celestial_bodies)
        self.commodity_prices = DataStructure(self.trade_data_client.get_prices(), locations=self.locations)
        self.commodities = DataStructure(self.trade_data_client.get_commodities(), prices=self.commodity_prices)
        self.resource_prices = DataStructure(self.mining_data_client.get_prices(), locations=self.locations)
        self.resources = DataStructure(self.mining_data_client.get_resources(), prices=self.resource_prices)
        return all((self.celestial_bodies, self.locations,
                    self.commodities, self.commodity_prices,
                    self.resources, self.resource_prices))

    def _save_cache(self, database_name, **kwargs):
        database = self.mongo_db.get_database(database_name)
        for name, value in kwargs.items():
            database.drop_collection(name)
            collection = database.create_collection(name)
            collection.insert_many(value)

    def _read_from_cache(self):
        self.celestial_bodies = DataStructure([doc for doc in self.mongo_db.places.celestial_bodies.find()])
        self.locations = DataStructure([doc for doc in self.mongo_db.places.locations.find()],
                                       parents=self.celestial_bodies)
        self.commodity_prices = DataStructure([doc for doc in self.mongo_db.trade.prices.find()],
                                              locations=self.locations)
        self.commodities = DataStructure([doc for doc in self.mongo_db.trade.commodities.find()],
                                         prices=self.commodity_prices)
        self.resource_prices = DataStructure([doc for doc in self.mongo_db.mining.prices.find()],
                                             locations=self.locations)
        self.resources = DataStructure([doc for doc in self.mongo_db.mining.resources.find()],
                                       prices=self.resource_prices)

    def update_data(self):
        if self._update_data_structure():
            if self.mongo_db:
                self._save_cache("places",
                                 celestial_bodies=self.celestial_bodies.get_list(),
                                 locations=self.locations.get_list())
                self._save_cache("trade",
                                 commodities=self.commodities.get_list(),
                                 prices=self.commodity_prices.get_list())
                self._save_cache("mining",
                                 resources=self.resources.get_list(),
                                 prices=self.resource_prices.get_list())
            return True
        elif self.mongo_db:
            self._read_from_cache()


class TradeAssistant(PricesStructure):

    def get_trade_routes(self, cargo=576, money=50000, start_location=None, end_location=None, avoid=(),
                         allow_illegal=True, max_commodities=3):
        all_routes = []
        for commodity in self.commodities.values():
            commodity_routes = commodity.get_routes(cargo, money, start_location, end_location, avoid)
            if commodity_routes and (commodity.legal or allow_illegal):
                all_routes.append(commodity_routes)

        if all_routes:
            all_routes.sort(key=lambda item: item.get('best_income'), reverse=True)

            return [(route['commodity_name'], route['table']) for route in all_routes[:max_commodities]]

    def send_trade_price_report(self, commodity_name, price, transaction_type, location_name):
        commodity = self.commodities.match_one(commodity_name)
        location = self.locations.match_one(location_name)
        if commodity and location:
            response = self.trade_data_client.update_price(commodity.id, price, location.id, transaction_type)
            if response.status_code == 204:
                return {'state': 'ok'}

        wrong = []
        if location is None:
            wrong.append(location_name)
        if commodity is None:
            wrong.append(commodity_name)
        return {
            'state': 'error',
            'wrong': ",".join(wrong)
        }

    def get_mining_prices(self, resource_name=None):
        if resource_name:
            resource = self.resources.match_exact_name(resource_name)
            if resource:
                return resource.get_prices_table()
        else:
            return [
                {
                    "Resource": resource.name,
                    "aUEC/unit": "%.3f" % resource.best_sell,
                    "Locations": "\n".join(resource.best_sell_locations)
                }
                for resource in self.resources.values() if resource.best_sell
            ]

    def send_mining_price_report(self, resource_name, cargo_percent, value,
                                 location_name="port olisar", full_cargo=32):
        resource = self.resources.match_one(resource_name)
        location = self.locations.match_one(location_name)
        if resource and location:
            unit_price = value / (cargo_percent * full_cargo)
            response = self.mining_data_client.update_price(resource.id, unit_price, location.id)
            if response.status_code == 204:
                return {'state': 'ok'}

        wrong = []
        if location is None:
            wrong.append(location_name)
        if resource is None:
            wrong.append(resource_name)
        return {
            'state': 'error',
            'wrong': ",".join(wrong)
        }


if __name__ == '__main__':
    ta = TradeAssistant()
    for _commodity_name, _routes_table in ta.get_trade_routes():
        print(_routes_table)
