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

    @staticmethod
    def ship_in_list(name, ship_list):
        for ship in ship_list:
            if name == ship['name']:
                return ship

    def get_flight_ready(self, ships):

        def get_loaner_basic_dict():
            new_loaner_dict = {
                'name': loaner['name'],
                'manufacturer': loaner['manufacturer'],
                'lti': "loaner",
            }
            if ship.get('owner'):
                new_loaner_dict['owner'] = ship['owner']
            return new_loaner_dict

        def get_new_loaner_dict():
            return {
                        'name': loaner['name'],
                        'manufacturer': loaner['manufacturer'],
                        'owners': ship['owners'],
                        'count': ship['count'],
                    }

        def get_loaner_summary_dict(new_loaner_dict):
            if new_loaner_dict is None:
                new_loaner_dict = get_new_loaner_dict()
            else:
                new_loaner_dict['count'] += ship['count']
                new_owners = [owner for owner in ship['owners'].split(", ") if owner not in new_loaner_dict['owners']]
                new_loaner_dict['owners'] = ", ".join([new_loaner_dict['owners']] + new_owners)
            return new_loaner_dict

        result = [ship for ship in ships if self.rsi_data.is_flight_ready(ship['name'])]
        for ship in ships:
            for loaner in self.rsi_data.get_loaners(ship['name']):
                if ship.get('lti') is None:
                    loaner_dict = self.ship_in_list(loaner['name'], result)
                    loaner_dict = get_loaner_summary_dict(loaner_dict)
                else:
                    loaner_dict = get_loaner_basic_dict()
                if loaner_dict not in result:
                    result.append(loaner_dict)
        return result

    def get_fleet_tables(self, args):
        if args.all_ships:
            ships = self.database_manager.get_all_ships_dicts()
        elif args.member:
            ships = self.database_manager.get_ships_dicts_by_member_name(args.member)
        else:
            ships = self.database_manager.get_ships_summary()

        if ships:
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

            headers = ["name", "manufacturer"]
            headers += [key for key in ships[0].keys() if key not in headers]

            return self.split_data_and_get_messages(ships, self.print_dict_table)

    def get_ship_for_member(self, ship):
        ship_name = ship.replace("lti", "").strip()
        ship_data = self.get_ship_data_from_name(ship_name)
        if ship_data and isinstance(ship_data, dict):
            ship_data['lti'] = "LTI" if ship[-3:].lower() == "lti" else ""
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
