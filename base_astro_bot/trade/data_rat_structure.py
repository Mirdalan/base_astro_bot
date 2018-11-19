from random import randint
import time

from .data_rat_client import TradeClient


class DataRatPrices:
    def __init__(self):
        self.client = TradeClient()

    @property
    def locations(self):
        return self.client.get_locations()

    @property
    def commodities(self):
        return self.client.get_commodities()

    @property
    def prices(self):
        return self.client.get_prices()

    @property
    def containers(self):
        return self.client.get_containers()

    def get_commodity_id(self, name):
        for item in self.commodities:
            if item['commodity_name'].lower() == name.lower():
                return item['id']

    def get_location_id(self, name):
        for item in self.locations:
            if item['location_name'].lower() == name.lower():
                return item['id']

    def get_price(self, commodity_id, location_id):
        for item in self.prices:
            if item['price_commodity'] == commodity_id and item['price_location'] == location_id:
                return item

    def _get_rat_update_structure(self, prices_dict):
        prices_for_rat = []
        for commodity_name, transactions in prices_dict.items():
            commodity_id = self.get_commodity_id(commodity_name)
            if commodity_id:
                for transaction, prices in transactions.items():
                    transaction_type = transaction.lower()
                    for price_string, locations in prices.items():
                        price = float(price_string)
                        for location_name in locations:
                            location_id = self.get_location_id(location_name)
                            if location_id:
                                message = "%s price for %s in %s" % (transaction_type, commodity_name, location_name)
                                prices_for_rat.append((commodity_id, price, location_id, transaction_type, message))
        return prices_for_rat

    def update(self, parent_prices):
        arguments_list = self._get_rat_update_structure(parent_prices)
        while True:
            try:
                idx = randint(0, len(arguments_list)-1)
                commodity_id, price, location_id, transaction_type, message = arguments_list.pop(idx)
                if self.get_price(commodity_id, location_id):
                    continue
                else:
                    self.client.update_price(commodity_id, price, location_id, transaction_type)
                    pause_time = 477 + randint(17, 250)
                    print(time.ctime())
                    print(message)
                    print("sleeping for %d minutes\n" % int(pause_time / 60))
                    time.sleep(pause_time)
            except IndexError:
                break

    def __bool__(self):
        return all((self.containers, self.locations, self.commodities, self.prices))
