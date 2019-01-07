from abc import ABC

from tabulate import tabulate

from ..base_mixin import BaseMixinClass


class TradeMixin(BaseMixinClass, ABC):
    trade = None

    @staticmethod
    def format_table(commodity_name, routes_table, add_header=True):
        table_string = tabulate(routes_table, tablefmt='presto')
        if add_header:
            line_length = max(len(line) for line in table_string.splitlines())
            header_position = int(line_length * 0.3)
            header_string = " commodity      |%s%s\n%s\n" % (" " * header_position, commodity_name, "-" * line_length)
            table_string = header_string + table_string
        if len(table_string) < 2000:
            return ["```%s```" % table_string]
        split_index = table_string.find("\n sell price")
        return [
            "```%s```" % table_string[:split_index],
            "```%s```" % table_string[split_index:]
        ]

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
            for formatted_table in self.format_table(commodity_name, routes_table):
                yield formatted_table

    def get_trade_prices_msgs(self, location_name):
        return self.split_data_and_get_messages(
            self.trade.get_trade_prices(location_name),
            self.print_dict_table
        )

    def report_trade_price(self, args):
        if args.commodity and args.price and args.transaction and args.location:
            try:
                result = self.trade.send_trade_price_report(args.commodity,
                                                            float(args.price),
                                                            args.transaction,
                                                            args.location)
                if result['state'] == 'ok':
                    return self.messages.success
                else:
                    return "\n".join([self.messages.something_went_wrong, result['wrong']])
            except ValueError:
                self.logger.warning("Wrong arguments given '%s'" % str(args))
        return self.messages.something_went_wrong

    def get_mining_messages(self, resource):
        return self.print_dict_table(self.trade.get_mining_prices(resource))

    def report_mining_price(self, args):
        if args.resource and args.percent and args.value and args.location:
            if args.cargo:
                cargo = args.cargo
            else:
                cargo = 32
            try:
                result = self.trade.send_mining_price_report(args.resource,
                                                             float(args.percent.replace("%", "")),
                                                             float(args.value),
                                                             args.location,
                                                             cargo)
                if result['state'] == 'ok':
                    return self.messages.success
                else:
                    return "\n".join([self.messages.something_went_wrong, result['wrong']])
            except ValueError:
                self.logger.warning("Wrong arguments given '%s'" % str(args))
        return self.messages.something_went_wrong

    def update_trade_data(self):
        if self.trade.update_data():
            return self.messages.success
        else:
            return self.messages.something_went_wrong
