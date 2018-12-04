from abc import ABC

from tabulate import tabulate

from ..base_mixin import BaseMixinClass


class TradeMixin(BaseMixinClass, ABC):
    trade = None

    def format_table(self, commodity_name, routes_table):
        table_string = tabulate(routes_table, tablefmt='presto')
        line_length = max(len(line) for line in table_string.splitlines())
        header_position = int(line_length * 0.3)
        header_string = " commodity      |%s%s\n%s\n" % (" " * header_position, commodity_name, "-" * line_length)
        table_string = "```%s%s```" % (header_string, table_string)
        if len(table_string) < 2000:
            return table_string
        return self.format_table(commodity_name, routes_table[:-1])

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

    def report_trade_price(self, args):
        if args.commodity_name and args.price and args.transaction_type and args.location_name:
            try:
                if self.trade.send_trade_price_report(args.commodity_name,
                                                      float(args.price),
                                                      args.transaction_type,
                                                      args.location_name):
                    return self.messages.success
            except ValueError:
                self.logger.warning("Wrong arguments given '%s'" % str(args))
        return self.messages.something_went_wrong

    def get_mining_messages(self, resource):
        return self.print_dict_table(self.trade.get_mining_prices(resource))

    def report_mining_price(self, args):
        if args.resource_name and args.percent and args.value and args.location_name:
            if args.cargo:
                cargo = args.cargo
            else:
                cargo = 32
            try:
                if self.trade.send_mining_price_report(args.resource_name,
                                                       float(args.percent.replace("%", "")),
                                                       float(args.value),
                                                       args.location_name,
                                                       cargo):
                    return self.messages.success
            except ValueError:
                self.logger.warning("Wrong arguments given '%s'" % str(args))
        return self.messages.something_went_wrong

    def update_trade_data(self):
        if self.trade.update_data():
            return self.messages.success
        else:
            return self.messages.something_went_wrong
