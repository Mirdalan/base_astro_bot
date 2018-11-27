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
        for commodity_name, routes_table in self.trade.get_trade_routes(cargo, budget, args.start_location,
                                                                        args.end_location, avoid, allow_illegal):
            table_string = " commodity      | %s\n" % commodity_name.upper()
            table_string += tabulate(routes_table, tablefmt='presto')
            yield table_string

    def update_trade_data(self):
        self.trade.update_database()
        return self.messages.success
