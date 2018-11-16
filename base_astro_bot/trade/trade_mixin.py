from abc import ABC

from tabulate import tabulate

from ..base_mixin import BaseMixinClass


class TradeMixin(BaseMixinClass, ABC):
    trade = None

    def get_trade_messages(self, args):
        budget = 1000000000
        cargo = 1000000000
        exclude = set()
        if args.budget:
            budget = float(args.budget)
            if budget < 1:
                budget = 1
        if args.cargo:
            cargo = int(args.cargo)
            if cargo < 1:
                cargo = 1
        if args.exclude:
            exclude.add(args.exclude)
        if args.legal:
            exclude.add("Jumptown")

        result = self.trade.get_trade_routes(cargo,
                                             budget,
                                             exclude=list(exclude),
                                             start_locations=args.start_location)
        return ["```%s```" % tabulate(list(route.items()), tablefmt="presto") for route in result]

    def update_trade_data(self):
        self.trade.update_database()
        return self.messages.success
