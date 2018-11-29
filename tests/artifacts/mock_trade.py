import os
import json


class BaseClient:

    @staticmethod
    def read_json(file_name):
        file_path = os.path.join(os.path.dirname(__file__), "trade_data", file_name + ".json")
        with open(file_path, 'r') as f:
            return json.loads(f.read())

    def get_containers(self):
        return self.read_json('containers')

    def get_locations(self):
        return self.read_json('locations')


class TradeClient(BaseClient):

    def get_commodities(self):
        return self.read_json('commodities')

    def get_prices(self):
        return self.read_json('commodity_prices')


class MiningClient(BaseClient):

    def get_resources(self):
        return self.read_json('resources')

    def get_prices(self):
        return self.read_json('resource_prices')
