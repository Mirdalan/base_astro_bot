from .prices import PricesStructure


class TradeAssistant(PricesStructure):

    def _get_item_deals(self, item_id, prices):
            pass

    def get_trade_routes(self, cargo, budget, avoid=None, start_location=None, end_location=None,
                         legal_only=True, max_commodities=3):
        start_locations_ids = self.locations.auto_match_names(start_location, avoid)
        end_locations_ids = self.locations.auto_match_names(end_location, avoid)

        routes = []
        for item_name, prices in self.prices.items():
            item_deals = self._get_item_deals(item_name, prices)

            if len(lowest_buy_locations) < 1 or len(highest_sell_locations) < 1:
                continue

            bought_units = cargo * 100
            spent_money = bought_units * lowest_buy
            if spent_money > budget:
                bought_units = budget / lowest_buy
                spent_money = budget

            money_after_trade = bought_units * highest_sell
            commodity_routes = [{
                'commodity': item_name,
                'invested money': spent_money,
                'income': round(money_after_trade - spent_money, 2),
                'bought units': round(bought_units, 2),
                'buy price': lowest_buy,
                'buy locations': "\n".join(["%s (%s)" % (location, self.locations[location])
                                            for location in lowest_buy_locations]),
                'sell price': highest_sell,
                'sell locations': "\n".join(["%s (%s)" % (location, self.locations[location])
                                            for location in highest_sell_locations]),
            }]

        routes.sort(key=lambda item: item.get('income'), reverse=True)
        return routes[:max_commodities]
