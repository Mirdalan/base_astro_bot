from abc import ABC

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
            yield self.trade.format_table(commodity_name, routes_table)

    def update_trade_data(self):
        if self.trade.update_data():
            return self.messages.success
        else:
            return self.messages.something_went_wrong
