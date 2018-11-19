import requests
import json

import settings


class BaseClient:
    base_url = "https://scm.oceandatarat.org:8443/scm-server/api/v1/"
    token = settings.SCM_TOKEN
    headers = {'authorization': settings.SCM_TOKEN}

    def get_containers(self):
        return requests.get(self.base_url + 'containers', headers=self.headers).json()

    def get_locations(self):
        return requests.get(self.base_url + 'locations', headers=self.headers).json()


class TradeClient(BaseClient):

    def get_commodities(self):
        return requests.get(self.base_url + 'commodities', headers=self.headers).json()

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
        return requests.get(self.base_url + 'commodity_prices', headers=self.headers).json()

    def update_price(self, commodity_id, price, location_id, transaction_type="buy"):
        payload = {
                    "price_type": transaction_type,
                    "price_location": location_id,
                    "price_commodity": commodity_id,
                    "price_unit_price": price
                  }
        return requests.patch(self.base_url + 'commodity_prices', json=payload, headers=self.headers)

    def add_transaction(self, commodity_id, price, units, location_id, transaction_type):
        payload = {
                    "transaction_type": transaction_type,
                    "transaction_location": location_id,
                    "transaction_commodity": commodity_id,
                    "transaction_units": units,
                    "transaction_unit_price": price
                  }
        return requests.post(self.base_url + 'commodity_transactions', json=payload, headers=self.headers)


class MiningClient(BaseClient):

    def get_resources(self):
        return requests.get(self.base_url + 'resources', headers=self.headers).json()

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
        return requests.get(self.base_url + 'resource_prices', headers=self.headers).json()

    def update_price(self, resource_id, price, location_id, transaction_type="buy"):
        payload = {
                    "price_type": transaction_type,
                    "price_location": location_id,
                    "price_resource": resource_id,
                    "price_unit_price": price
                  }
        return requests.patch(self.base_url + 'resource_prices', json=payload, headers=self.headers)


def save_to_temp_file(text, file_name="temp.txt"):
    with open(file_name, 'w') as f:
        f.write(text)


def save_to_temp_json(structure, file_name="temp"):
    text = json.dumps(structure, indent=4)
    save_to_temp_file(text, file_name + ".json")


if __name__ == '__main__':
    cli = TradeClient()
    save_to_temp_json(cli.get_containers(), "containers")
    save_to_temp_json(cli.get_locations(), "locations")
