from operator import itemgetter
import threading
import time

from tabulate import tabulate
import pafy

from .utils.attachments_downloader import DiscordAttachmentHandler
from .database import DatabaseManager
from .utils.my_logger import MyLogger
from .rsi_data import RsiDataParser, RsiMixin
from .trade import TradeAssistant, TradeMixin
import settings


class BaseBot(RsiMixin, TradeMixin):
    main_channel_id = settings.CHANNELS['main']
    messages = settings.messages
    max_characters = settings.MESSAGE_MAX_CHARACTERS
    max_ships = settings.MESSAGE_MAX_SHIPS
    ship_data_headers = settings.SHIP_DATA_HEADERS

    def __init__(self):
        self.logger = MyLogger(log_file_name=settings.LOG_FILE, logger_name=settings.LOGGER_NAME, prefix="[BOT]")

        self.channel_main = self._get_channel_instance(self.main_channel_id)
        self.bot_user = self._get_bot_user()

        self.database_manager = DatabaseManager(log_file=settings.LOG_FILE)

        self.attachments_handler = DiscordAttachmentHandler()

        self.rsi_data = RsiDataParser(7600, log_file=settings.LOG_FILE, database_manager=self.database_manager)
        self.report_ship_price_list = settings.REPORT_SHIP_PRICE_LIST

        self.monitoring_thread = threading.Thread(target=self.monitoring_procedure)
        self.monitoring_thread.start()

        self.trade = TradeAssistant(log_file=settings.LOG_FILE)

        self.help_message = self._get_help_message()

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
    def print_dict_table(items, table_format="presto"):
        return "```%s```" % tabulate(items, headers='keys', tablefmt=table_format)

    @staticmethod
    def print_list_table(items, table_format="presto"):
        return "```%s```" % tabulate(items, tablefmt=table_format)

    def split_data_and_get_messages(self, items, get_message_function, *args, **kwargs):
        message = get_message_function(items, *args, **kwargs)
        if len(message) < self.max_characters:
            messages = [message]
        else:
            half_length = int(len(items) * 0.5)
            messages = self.split_data_and_get_messages(items[:half_length], get_message_function, *args, **kwargs)
            messages += self.split_data_and_get_messages(items[half_length:], get_message_function, *args, **kwargs)
        return messages

    def update_fleet(self, attachments, author):
        invalid_ships = None
        for file in attachments.values():
            self.logger.debug("Checking file %s." % file.filename)
            try:
                if file.filename == "shiplist.json":
                    self.logger.debug("Getting ships list.")
                    ships = self.attachments_handler.get_ship_list(file.url, self.logger)
                    ships, invalid_ships = self.rsi_data.verify_ships(ships)
                    self.database_manager.update_member_ships(ships, author)

            except Exception as unexpected_exception:
                self.logger.error(str(unexpected_exception))
        return invalid_ships

    def clear_member_fleet(self, author):
        self.database_manager.update_member_ships([], author)
        return self.database_manager.get_ships_by_member_name(author.username)

    def get_fleet_tables(self, args):
        if args.all_ships:
            ships = self.database_manager.get_all_ships_dicts()
        else:
            ships = self.database_manager.get_ships_summary()

        if args.filter:
            filters = args.filter.split(",")
            for item in filters:
                key, expected_value = item.split("=")
                ships = [ship for ship in ships if expected_value.lower() in str(ship[key]).lower()]

        if args.order_by:
            columns = args.order_by.split(",")
            columns.reverse()
        else:
            columns = ["name", "manufacturer"]
        for column in columns:
            ships = sorted(ships, key=itemgetter(column))
        if args.descending:
            ships.reverse()

        return self.split_data_and_get_messages(ships, self.print_dict_table)

    def get_ship_for_member(self, ship):
        ship_name = ship.replace("lti", "").strip()
        ship_data = self.get_ship_data_from_name(ship_name)
        if ship_data and isinstance(ship_data, dict):
            ship_data['lti'] = ship[-3:].lower() == "lti"
            return ship_data

    def add_member_ship(self, ship_query, author):
        ship_data = self.get_ship_for_member(ship_query)
        if ship_data:
            self.database_manager.add_one_ship(ship_data, author)
            for message in self.iterate_updated_ships_messages(author):
                yield message
        else:
            yield self.messages.ship_not_exists % self.mention_user(author)

    def remove_member_ship(self, ship_query, author):
        ship_data = self.get_ship_for_member(ship_query)
        if ship_data:
            if self.database_manager.remove_one_ship(ship_data, author):
                for message in self.iterate_updated_ships_messages(author):
                    yield message
            else:
                yield self.messages.member_ship_not_found % self.mention_user(author)
        else:
            yield self.messages.ship_not_exists % self.mention_user(author)

    def iterate_invalid_ships_messages(self, author, invalid_ships):
        yield self.messages.member_ships_invalid % (self.mention_user(author))
        for message in self.split_data_and_get_messages(invalid_ships, self.print_dict_table, table_format="rst"):
            yield message

    def iterate_updated_ships_messages(self, author):
        yield self.messages.member_ships_modified % (self.mention_user(author))
        for message in self.get_member_fleet(author.username):
            yield message

    def get_member_fleet(self, member_name):
        ships = self.database_manager.get_ships_dicts_by_member_name(member_name)
        if ships:
            for message in self.split_data_and_get_messages(ships, self.print_dict_table, table_format="rst"):
                yield message
        else:
            yield self.messages.member_not_found

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
            self.monitor_current_releases()
            self.monitor_forum_threads()
            self.monitor_youtube_channel()
            self.report_ship_price()
            time.sleep(300)
