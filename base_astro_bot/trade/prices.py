from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import settings
from ..utils import MyLogger
from ..database import DatabaseManager


class PricesStructure:
    spreadsheet_id = settings.TRADE_SPREADSHEET_ID
    commodities = settings.TRADE_COMMODITIES

    def __init__(
            self,
            release=settings.TRADE_SC_RELEASE,
            cells_range=settings.TRADE_SPREADSHEET_CELLS_RANGE,
            log_file="trade_assistant.log",
            database_manager=None
    ):
        self._log_file = log_file
        self.logger = MyLogger(log_file_name=self._log_file, logger_name="Trade Assistant logger", prefix="[TRADE]")
        self.release = release
        self.range_name = '%s!%s' % (release, cells_range)
        self.database = self.get_given_or_new_database_manager(database_manager)
        self.locations = None
        self.prices = {}
        self._value_type_row = None
        self._initiate_database()

    def get_given_or_new_database_manager(self, database_manager):
        if database_manager:
            return database_manager
        else:
            return DatabaseManager(log_file=self._log_file)

    @staticmethod
    def _fill_missing_blank_cells(values):
        full_length = None
        for row in values:
            if 'Buy' in row:
                full_length = len(row)
                break
        for row in values:
            too_short_by = full_length - len(row)
            row += [''] * too_short_by
        return values

    def _get_spreadsheet_rows(self):
        store = file.Storage('google_token.json')
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets('google_credentials.json', settings.TRADE_GOOGLE_SCOPES)
            credentials = tools.run_flow(flow, store)
        service = build('sheets', 'v4', http=credentials.authorize(Http()))

        result = service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id,
                                                     range=self.range_name).execute()
        return self._fill_missing_blank_cells(result.get('values', []))

    @staticmethod
    def _populate_merged_cells(row):
        populated_row = []
        previous_item = None
        for item in row:
            if previous_item and item == '':
                populated_row.append(previous_item)
            else:
                populated_row.append(item)
                previous_item = item
        return populated_row

    def _build_locations(self, locations, celestial_bodies):
        self.locations = {
            location: celestial_bodies[index]
            for index, location in enumerate(locations) if location
        }

    def _row_contains_price(self, index):
        return 'Buy' in self._value_type_row[index] or 'Sell' in self._value_type_row[index]

    def _download_data_structure(self):
        values = self._get_spreadsheet_rows()
        locations, celestial_bodies, self._value_type_row = None, None, None
        if values:
            for row in values:
                if 'CRUSADER' in row:
                    celestial_bodies = self._populate_merged_cells(row)
                elif 'Port Olisar' in row:
                    if celestial_bodies:
                        self._build_locations(row, celestial_bodies)
                    locations = self._populate_merged_cells(row)
                elif 'Profit' in row:
                    self._value_type_row = row
                elif locations and celestial_bodies and self._value_type_row and row[0].strip() in self.commodities:
                    item_name = row[0]
                    item_prices = {}
                    for index, location in enumerate(locations):
                        if row[index] and self._row_contains_price(index):
                            price = str(float(row[index].replace(",", ".")))
                            transaction = self._value_type_row[index]
                            if item_prices.get(transaction):
                                if item_prices[transaction].get(price):
                                    item_prices[transaction][price].append(location)
                                else:
                                    item_prices[transaction][price] = [location]
                            else:
                                item_prices[transaction] = {price: [location]}
                    self.prices[item_name] = item_prices

    def _initiate_database(self):
        stored_data = self.database.get_trade_data()
        if stored_data:
            self.locations, self.prices = stored_data
        else:
            self.update_database()

    def update_database(self):
            self._download_data_structure()
            self.database.save_trade_data(self.locations, self.prices)
