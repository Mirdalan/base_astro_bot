from abc import ABC

from tabulate import tabulate

from ..base_mixin import BaseMixinClass


class TradeMixin(BaseMixinClass, ABC):
    trade = None

    def get_trade_messages(self, args):
        budget = 1000000000
        cargo = 1000000000
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

        result = self.trade.get_trade_routes(cargo, budget, avoid, args.start_location, args.end_location, args.legal)
        return [self.print_dict_table(route, tablefmt="presto") for route in result]

    def update_trade_data(self):
        self.trade.update_database()
        return self.messages.success
