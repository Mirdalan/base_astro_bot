import threading
import time

from tabulate import tabulate
from pymongo import MongoClient
import pafy
from requests.exceptions import RequestException

from .utils import MyLogger
from .database import DatabaseManager
from .rsi_data import RsiDataParser, RsiMixin
from .trade import TradeAssistant, TradeMixin
from .fleet import FleetMixin
import settings


class BaseBot(RsiMixin, TradeMixin, FleetMixin):
    main_channel_id = settings.CHANNELS['main']
    messages = settings.messages
    max_characters = settings.MESSAGE_MAX_CHARACTERS
    max_ships = settings.MESSAGE_MAX_SHIPS
    ship_data_headers = settings.SHIP_DATA_HEADERS
    mongo_uri = settings.MONGO_CONNECTION_STRING

    def __init__(self):
        self.logger = MyLogger(log_file_name=settings.LOG_FILE, logger_name=settings.LOGGER_NAME, prefix="[BOT]")

        self.channel_main = self._get_channel_instance(self.main_channel_id)
        self.bot_user = self._get_bot_user()

        self.database_manager = DatabaseManager(log_file=settings.LOG_FILE)
        self.mongo = MongoClient(self.mongo_uri)

        self.rsi_data = RsiDataParser(7600, log_file=settings.LOG_FILE, database_manager=self.database_manager)
        self.report_ship_price_list = settings.REPORT_SHIP_PRICE_LIST

        self.trade = TradeAssistant(log_file=settings.LOG_FILE, mongo_client=self.mongo)

        self.monitoring_thread = threading.Thread(target=self.monitoring_procedure)
        self.monitoring_thread.start()

        self.help_messages = self._get_help_message()

    def _get_channel_instance(self, channel_id):
        raise NotImplementedError

    def _get_help_message(self):
        raise NotImplementedError

    def _get_bot_user(self):
        raise NotImplementedError

    @staticmethod
    def mention_user(user):
        raise NotImplementedError

    @staticmethod
    def mention_channel(channel):
        raise NotImplementedError

    def get_author_if_given(self, author):
        if author:
            return self.mention_user(author)
        else:
            return ""

    @staticmethod
    def print_dict_table(items, table_format="presto", **kwargs):
        return "```%s```" % tabulate(items, headers='keys', tablefmt=table_format, **kwargs)

    @staticmethod
    def print_list_table(items, table_format="presto", **kwargs):
        return "```%s```" % tabulate(items, tablefmt=table_format, **kwargs)

    def split_data_and_get_messages(self, items, get_message_function, *args, **kwargs):
        message = get_message_function(items, *args, **kwargs)
        if len(message) < self.max_characters:
            messages = [message]
        else:
            half_length = int(len(items) * 0.5)
            messages = self.split_data_and_get_messages(items[:half_length], get_message_function, *args, **kwargs)
            messages += self.split_data_and_get_messages(items[half_length:], get_message_function, *args, **kwargs)
        return messages

    def report_ship_price(self):
        for ship_name, price_limit in self.report_ship_price_list:
            ship_data = self.rsi_data.get_ship(ship_name)
            if ship_data is None:
                self.channel_main.send_message(self.messages.ship_from_report_not_found % ship_name)
            else:
                current_price = float(ship_data["price"][1:])
                if current_price > price_limit:
                    self.channel_main.send_message(self.messages.ship_price_report % (ship_name, ship_data["price"]))
                    self.report_ship_price_list.remove((ship_name, price_limit))

    def monitor_current_releases(self):
        current_releases = self.rsi_data.get_updated_versions()
        new_version_released = self.database_manager.update_versions(current_releases)

        if new_version_released:
            new_release_message = self.update_releases()
            new_release_message = self.messages.new_version % new_release_message
            self.channel_main.send_message(new_release_message)

    def monitor_forum_threads(self):
        new_threads = self.rsi_data.get_forum_release_messages()
        if new_threads:
            self.channel_main.send_message(self.messages.new_version % "")
            for thread in new_threads:
                self.channel_main.send_message(thread)

    def monitor_youtube_channel(self):
        latest_video_url = pafy.get_channel("RobertsSpaceInd").uploads[0].watchv_url
        if self.database_manager.rsi_video_is_new(latest_video_url):
            self.channel_main.send_message(latest_video_url)

    def monitoring_procedure(self):
        while True:
            try:
                self.monitor_current_releases()
                self.monitor_forum_threads()
                self.monitor_youtube_channel()
                self.report_ship_price()
                self.trade.update_data()
            except RequestException:
                self.logger.warning("Network connection error. Sleeping a bit longer.")
                time.sleep(1200)
            time.sleep(300)
