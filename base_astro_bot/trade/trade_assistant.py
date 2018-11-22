from .prices import PricesStructure
from . import data_structure


class TradeAssistant(PricesStructure):

    @staticmethod
    def _get_best_deal(buy_prices, sell_prices):
        return max(sell_price - buy_price for buy_price in buy_prices for sell_price in sell_prices)

    def get_trade_routes(self, cargo, budget, avoid=None, start_location=None, end_location=None,
                         legal_only=True, max_commodities=3):
        start_locations_ids = self.locations.auto_match_names(start_location, avoid)
        end_locations_ids = self.locations.auto_match_names(end_location, avoid)

        bought_units = cargo * 100
        spent_money = bought_units * lowest_buy
        if spent_money > budget:
            bought_units = budget / lowest_buy
            spent_money = budget

        def _get_item_deals(item_id, prices):
            commodity_routes = []
            buy_prices, sell_prices = [], []
            for price in prices:   # type: data_structure.CommodityPrice
                if price.type == "buy" and price.location.id in start_locations_ids:
                    buy_prices.append(price)
                elif price.type == "sell" and price.location.id in end_locations_ids:
                    sell_prices.append(price)

                route_data = {
                    'commodity': item_id,
                    'invested money': spent_money,
                    'income': round(money_after_trade - spent_money, 2),
                    'bought units': round(bought_units, 2),
                    'buy price': lowest_buy,
                    'buy locations': "\n".join(["%s (%s)" % (location, self.locations[location])
                                                for location in lowest_buy_locations]),
                    'sell price': highest_sell,
                    'sell locations': "\n".join(["%s (%s)" % (location, self.locations[location])
                                                for location in highest_sell_locations]),
                }

                commodity_routes.append({
                    'best_income': self._get_best_deal(buy_prices, sell_prices),
                    'table': route_data
                })

        routes = []
        for item_id, prices in self.prices.items():
            item_deals = self._get_item_deals(item_id, prices)

            if len(lowest_buy_locations) < 1 or len(highest_sell_locations) < 1:
                continue


            money_after_trade = bought_units * highest_sell

        routes.sort(key=lambda item: item.get('income'), reverse=True)
        return routes[:max_commodities]
