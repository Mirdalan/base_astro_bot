from abc import ABC
from operator import itemgetter

from ..base_mixin import BaseMixinClass


class FleetMixin(BaseMixinClass, ABC):
    attachments_handler = None

    def get_ship_data_from_name(self, ship_name):
        raise NotImplementedError

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
