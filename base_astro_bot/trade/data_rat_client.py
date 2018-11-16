from datetime import date

import requests


class DataClient:
    base_url = "https://scm.oceandatarat.org:8443/scm-server/api/v1/"

    def get_commodities(self):
        return requests.get(self.base_url + 'commodities').json()

    def get_locations(self):
        return requests.get(self.base_url + 'locations').json()

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
        return requests.get(self.base_url + 'commodity_prices').json()

    def update_price(self, commodity_id, price, location_id, transaction_type="buy"):
        payload = {
                    "price_type": transaction_type,
                    "price_location": location_id,
                    "price_date": date.today().strftime("%Y-%m-%d"),
                    "price_commodity": commodity_id,
                    "price_unit_price": price
                  }
        return requests.patch(self.base_url + 'commodity_prices', json=payload).json()

    def add_transaction(self, commodity_id, price, units, location_id, transaction_type):
        payload = {
                    "transaction_type": transaction_type,
                    "transaction_location": location_id,
                    "transaction_commodity": commodity_id,
                    "transaction_units": units,
                    "transaction_unit_price": price
                  }
        return requests.post(self.base_url + 'commodity_transactions', json=payload).json()


if __name__ == '__main__':
    print(DataClient().get_locations())
