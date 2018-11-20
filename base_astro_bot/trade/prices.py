from ..utils import MyLogger
from ..database import DatabaseManager
from .data_structure import DataStructure
from .data_rat_structure import DataRatPrices


class PricesStructure:

    def __init__(self, log_file="trade_assistant.log", database_manager=None):
        self._log_file = log_file
        self.logger = MyLogger(log_file_name=self._log_file, logger_name="Trade Assistant logger", prefix="[TRADE]")
        self.database = self._get_existing_or_new_database_manager(database_manager)
        self.data_rat = DataRatPrices()
        self.celestial_bodies = None   # type: DataStructure
        self.locations = None   # type: DataStructure
        self.commodities = None   # type: DataStructure
        self.prices = None   # type: DataStructure
        self.update_database()

    def update_rat(self):
        self.data_rat.update(self.prices)

    def _get_existing_or_new_database_manager(self, database_manager):
        if database_manager:
            return database_manager
        else:
            return DatabaseManager(log_file=self._log_file)

    def _update_data_structure(self):
        self.celestial_bodies = DataStructure(self.data_rat.containers)
        self.locations = DataStructure(self.data_rat.locations, parents=self.celestial_bodies)
        self.commodities = DataStructure(self.data_rat.commodities)
        self.prices = DataStructure(self.data_rat.prices, commodities=self.commodities, locations=self.locations)

    def update_database(self):
        self._update_data_structure()
        self.database.save_trade_data(self.locations, self.prices)
