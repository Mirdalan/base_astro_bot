from abc import ABC

from tabulate import tabulate

from .road_map_mixin import RoadMapMixin


class RsiMixin(RoadMapMixin, ABC):

    def get_ship_data_from_name(self, ship_name):
        return self.rsi_data.get_ship_data_from_name(ship_name)

    @staticmethod
    def get_ship_price_message(ship):
        return "*%s*  **%s**, price:  %s (+ VAT)" % (ship["manufacturer_code"], ship["name"], ship["price"])

    def get_ship_prices_lines(self, found_ships):
        prices_lines = []
        for ship in found_ships:
            try:
                prices_lines.append(self.get_ship_price_message(ship))
            except KeyError:
                prices_lines.append(self.messages.ship_price_unknown % (ship["manufacturer_code"], ship["name"]))
        return prices_lines

    def iterate_ship_prices(self, query, author=None):
        found_ships = self.rsi_data.get_ships_by_query(query)
        if 0 < len(found_ships) < self.max_ships:
            price_lines = self.get_ship_prices_lines(found_ships)
            for message in self.split_data_and_get_messages(price_lines, lambda lines: "\n".join(lines)):
                yield message
        else:
            yield self.messages.ship_not_exists % self.get_author_if_given(author)

    def format_ship_data(self, ship):
        table = [[key, ship.get(key, "unknown")] for key in self.ship_data_headers]
        return "%s\n```%s```\n" % (self.rsi_data.base_url + ship['url'], tabulate(table))

    def compare_ships_data(self, ships):
        table = [[key] for key in self.ship_data_headers]
        for ship in ships:
            if ship:
                for row in table:
                    row.append(ship.get(row[0], "unknown"))
        return "\n```%s```\n" % tabulate(table)

    def split_compare_if_too_long(self, ships):
        return self.split_data_and_get_messages(ships, self.compare_ships_data)

    def iterate_ship_info(self, query, author=None):
        found_ship = self.get_ship_data_from_name(query)
        if isinstance(found_ship, list) and (1 < len(found_ship) < self.max_ships):
            for message in self.split_compare_if_too_long(found_ship):
                yield message
        elif isinstance(found_ship, dict):
            yield self.format_ship_data(found_ship)
        else:
            yield self.messages.ship_not_exists % self.get_author_if_given(author)

    def iterate_ships_comparison(self, query, author=None):
        names = query.split(",")
        found_ships = []
        for name in names:
            for ship_data in self.rsi_data.get_ships_by_query(name.strip()):
                found_ships.append(ship_data)
        if isinstance(found_ships, list) and len(found_ships) < self.max_ships:
            for message in self.split_compare_if_too_long(found_ships):
                yield message
        else:
            yield self.messages.ship_not_exists % self.get_author_if_given(author)

    def update_releases(self):
        current_releases = self.rsi_data.get_updated_versions()
        self.database_manager.update_versions(current_releases)
        return "PU Live: %s\nPTU: %s\n" % (current_releases.get('live'), current_releases.get('ptu'))
