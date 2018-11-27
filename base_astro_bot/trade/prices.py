from base_astro_bot.utils import MyLogger
from base_astro_bot.database import DatabaseManager
from base_astro_bot.trade.data_structure import DataStructure
from base_astro_bot.trade.data_rat_client import TradeClient


class PricesStructure:

    def __init__(self, log_file="trade_assistant.log", database_manager=None):
        self._log_file = log_file
        self.logger = MyLogger(log_file_name=self._log_file, logger_name="Trade Assistant logger", prefix="[TRADE]")
        self.database = self._get_existing_or_new_database_manager(database_manager)
        self.data_rat = TradeClient()
        self.celestial_bodies = None   # type: DataStructure
        self.locations = None   # type: DataStructure
        self.commodities = None   # type: DataStructure
        self.prices = None   # type: DataStructure
        self.update_database()

    def _get_existing_or_new_database_manager(self, database_manager):
        if database_manager:
            return database_manager
        else:
            return DatabaseManager(log_file=self._log_file)

    def _update_data_structure(self):
        self.celestial_bodies = DataStructure(self.data_rat.get_containers())
        self.locations = DataStructure(self.data_rat.get_locations(), parents=self.celestial_bodies)
        self.prices = DataStructure(self.data_rat.get_prices(), locations=self.locations)
        self.commodities = DataStructure(self.data_rat.get_commodities(), prices=self.prices)

    def update_database(self):
        self._update_data_structure()
        self.database.save_trade_data(self.celestial_bodies, self.locations, self.commodities, self.prices)


class TradeAssistant(PricesStructure):

    def get_trade_routes(self, cargo=576, money=50000, start_location=None, end_location=None, avoid=(),
                         allow_illegal=True, max_commodities=3):
        all_routes = [commodity.get_routes(cargo, money, start_location, end_location, avoid)
                      for commodity in self.commodities.values() if allow_illegal or commodity.legal]
        all_routes.sort(key=lambda item: item.get('best_income'), reverse=True)

        return [route['routes'] for route in all_routes[:max_commodities]]


if __name__ == '__main__':
    from tabulate import tabulate
    ta = TradeAssistant()
    for single_route in ta.get_trade_routes():
        output = tabulate(single_route, headers='keys', tablefmt='presto')
        print(output)
