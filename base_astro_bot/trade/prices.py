from ..utils import MyLogger
from ..database import DatabaseManager
from .data_rat_structure import DataRatPrices


class PricesStructure:

    def __init__(
            self,
            log_file="trade_assistant.log",
            database_manager=None
    ):
        self._log_file = log_file
        self.logger = MyLogger(log_file_name=self._log_file, logger_name="Trade Assistant logger", prefix="[TRADE]")
        self.database = self._get_existing_or_new_database_manager(database_manager)
        self.data_rat = DataRatPrices()
        self.celestial_bodies = {}
        self.locations = {}
        self.commodities = {}
        self.prices = {}
        self._value_type_row = None
        self._initiate_database()

    def update_rat(self):
        self.data_rat.update(self.prices)

    def _get_existing_or_new_database_manager(self, database_manager):
        if database_manager:
            return database_manager
        else:
            return DatabaseManager(log_file=self._log_file)

    def _initiate_database(self):
        self.update_database()

    def _get_locations_structure(self):
        result = {}
        for item in self.data_rat.containers:
            item['container_name'] = self.celestial_bodies[item['location_container']]['container_name']
            result[item['id']] = item
        return result

    def _update_data_structure(self):
        self.celestial_bodies = {item['id']: item for item in self.data_rat.containers}
        self.locations = self._get_locations_structure()
        self.commodities = {item['id']: item for item in self.data_rat.commodities}

        for price_structure in self.data_rat.prices:
            item_prices = {}
            # price_structure = {
            #             "price_commodity": "5bb6a7f7574bd8753cce3f0f",
            #             "price_location": "5bb75803b6551685e87381f6",
            #             "price_date": "2018-11-18T19:53:35.226Z",
            #             "price_type": "sell",
            #             "price_unit_price": 1.02,
            #             "id": "5bef881a12c026d3ac9f506c"
            #         },
            item_id = price_structure['price_commodity']
            item_name = self.commodities[item_id]['commodity_name']
            price = str(price_structure['price_unit_price'])
            transaction = price_structure['price_type']
            location_id = price_structure['price_location']
            if item_prices.get(transaction):
                if item_prices[transaction].get(price):
                    item_prices[transaction][price].append(location_id)
                else:
                    item_prices[transaction][price] = [location_id]
            else:
                item_prices[transaction] = {price: [location_id]}
            self.prices[item_name] = item_prices

    def update_database(self):
            self._update_data_structure()
            self.database.save_trade_data(self.locations, self.prices)
