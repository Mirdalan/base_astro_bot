from .prices import PricesStructure


class TradeAssistant(PricesStructure):

    def get_trade_routes(self, cargo=576, money=50000, start_location=None, end_location=None, avoid=(),
                         allow_illegal=True, max_commodities=3):
        all_routes = [commodity.get_routes(cargo, money, start_location, end_location, avoid)
                      for commodity in self.commodities.values() if allow_illegal or commodity.legal]
        all_routes.sort(key=lambda item: item.get('best_income'), reverse=True)

        return [route['routes'] for route in all_routes[:max_commodities]]
