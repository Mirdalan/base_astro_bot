from abc import ABC

from tabulate import tabulate

from ..base_mixin import BaseMixinClass


class TradeMixin(BaseMixinClass, ABC):
    trade = None

    def get_trade_messages(self, args):
        budget = 50000
        cargo = 576
        avoid = []
        if args.budget:
            budget = float(args.budget)
            if budget < 1:
                budget = 1
        if args.cargo:
            cargo = int(args.cargo)
            if cargo < 1:
                cargo = 1
        if args.avoid:
            avoid = [item.strip() for item in args.avoid.split(",")]

        allow_illegal = not args.legal

        arguments = (cargo, budget, args.start_location, args.end_location, avoid, allow_illegal)
        for commodity_name, routes_table in self.trade.get_trade_routes(*arguments):
            yield self.format_table(commodity_name, routes_table)

    def format_table(self, commodity_name, routes_table):
        table_string = tabulate(routes_table, tablefmt='presto')
        line_length = max(len(line) for line in table_string.splitlines())
        header_position = int(line_length * 0.3)
        header_string = " commodity      |%s%s\n%s\n" % (" " * header_position, commodity_name, "-" * line_length)
        table_string = "```%s%s```" % (header_string, table_string)
        if len(table_string) < 2000:
            return table_string
        return self.format_table(commodity_name, routes_table[:-1])

    def get_mining_messages(self, resource):
        return self.print_dict_table(self.trade.get_mining_prices(resource))

    def update_trade_data(self):
        if self.trade.update_data():
            return self.messages.success
        else:
            return self.messages.something_went_wrong
