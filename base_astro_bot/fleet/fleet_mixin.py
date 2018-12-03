from abc import ABC
from operator import itemgetter

from ..base_mixin import BaseMixinClass


class FleetMixin(BaseMixinClass, ABC):
    rsi_data = None

    def get_ship_data_from_name(self, ship_name):
        raise NotImplementedError

    def clear_member_fleet(self, author):
        self.database_manager.update_member_ships([], author)
        return self.database_manager.get_ships_by_member_name(author.username)

    def get_flight_ready(self, ships):
        result = []
        for ship in ships:
            if self.rsi_data.is_flight_ready(ship['name']):
                result.append(ship)
            for loaner in self.rsi_data.get_loaners(ship['name']):
                loaner_dict = {
                    'name': loaner['name'],
                    'manufacturer': loaner['manufacturer']
                }
                if ship.get('owner'):
                    loaner_dict['owner'] = ship['owner']
                    loaner_dict['lti'] = "loaner"
                result.append(loaner_dict)
        return result

    def get_fleet_tables(self, args):
        if args.all_ships:
            ships = self.database_manager.get_all_ships_dicts()
        elif args.member:
            ships = self.database_manager.get_ships_dicts_by_member_name(args.member)
        else:
            ships = self.database_manager.get_ships_summary()

        if args.flight_ready:
            ships = self.get_flight_ready(ships)

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

    def get_member_fleet(self, member_name, flight_ready=False):
        ships = self.database_manager.get_ships_dicts_by_member_name(member_name)

        if ships:
            if flight_ready:
                ships = self.get_flight_ready(ships)
            for message in self.split_data_and_get_messages(ships, self.print_dict_table, table_format="rst"):
                yield message
        else:
            yield self.messages.member_not_found
