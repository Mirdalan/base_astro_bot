import requests
import json

import settings


def handles_request_exception(func):
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException:
            return None
    return func_wrapper


class BaseClient:
    base_url = "https://scm.oceandatarat.org:8443/scm-server/api/v1/"
    token = settings.SCM_TOKEN
    headers = {'authorization': settings.SCM_TOKEN}

    @handles_request_exception
    def get_request(self, endpoint):
        return requests.get(self.base_url + endpoint, headers=self.headers).json()

    @handles_request_exception
    def patch_request(self, endpoint, payload):
        return requests.patch(self.base_url + endpoint, json=payload, headers=self.headers)

    @handles_request_exception
    def post_request(self, endpoint, payload):
        return requests.post(self.base_url + endpoint, json=payload, headers=self.headers)

    def get_containers(self):
        return self.get_request('containers')

    def get_locations(self):
        return self.get_request('locations')


class TradeClient(BaseClient):

    def get_commodities(self):
        return self.get_request('commodities')

    def get_prices(self):
        """
        :return: [
                  {
                    "id": {},
                    "price_type": "buy/sell",
                    "price_location": "string",
                    "price_date": "2018-11-15",
                    "price_commodity": "string",
                    "price_unit_price": 0
                  }
                ]
        """
        return self.get_request('commodity_prices')

    def update_price(self, commodity_id, price, location_id, transaction_type="buy"):
        payload = {
                    "price_type": transaction_type,
                    "price_location": location_id,
                    "price_commodity": commodity_id,
                    "price_unit_price": price
                  }
        return self.patch_request('commodity_prices', payload)

    def add_transaction(self, commodity_id, price, units, location_id, transaction_type):
        payload = {
                    "transaction_type": transaction_type,
                    "transaction_location": location_id,
                    "transaction_commodity": commodity_id,
                    "transaction_units": units,
                    "transaction_unit_price": price
                  }
        return self.post_request('commodity_transactions', payload)


class MiningClient(BaseClient):

    def get_resources(self):
        return self.get_request('resources')

    def get_prices(self):
        """
        :return: [
                  {
                    "id": {},
                    "price_type": "buy/sell",
                    "price_location": "string",
                    "price_date": "2018-11-15",
                    "price_resource": "string",
                    "price_unit_price": 0
                  }
                ]
        """
        return self.get_request('resource_prices')

    def update_price(self, resource_id, price, location_id):
        payload = {
                    "price_type": "sell",
                    "price_location": location_id,
                    "price_resource": resource_id,
                    "price_unit_price": price
                  }
        return self.patch_request('resource_prices', payload)


def save_to_temp_file(text, file_name="temp.txt"):
    with open(file_name, 'w') as f:
        f.write(text)


def save_to_temp_json(structure, file_name="temp"):
    text = json.dumps(structure, indent=4)
    save_to_temp_file(text, file_name + ".json")


if __name__ == '__main__':
    cli = TradeClient()
    save_to_temp_json(cli.get_prices(), "trade_prices")
    # cli = MiningClient()
    # save_to_temp_json(cli.get_resources(), "mining_resources")
