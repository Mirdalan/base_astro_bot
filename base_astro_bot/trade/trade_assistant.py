from .prices import PricesStructure


class TradeAssistant(PricesStructure):

    @staticmethod
    def _get_filtered_locations(start_locations, lowest_buy_locations):
        new_buy_locations = []
        for location in lowest_buy_locations:
            if location in start_locations:
                new_buy_locations.append(location)
        return new_buy_locations

    def _get_allowed_locations(self, query):
        query = query.lower()
        return [location for location in self.locations.keys()
                if query in location.lower()
                or query in self.locations[location].lower()]

    @staticmethod
    def _exclude_locations(lowest_buy_locations, highest_sell_locations, exclude):
        assert isinstance(exclude, list)
        for no_go_location in exclude:
            if no_go_location in lowest_buy_locations:
                lowest_buy_locations.remove(no_go_location)
            if no_go_location in highest_sell_locations:
                highest_sell_locations.remove(no_go_location)

    def get_trade_routes(self, full_bay, budget, exclude=None, start_locations=None, number_of_routes=3):
        if start_locations:
            start_locations = self._get_allowed_locations(start_locations)

        routes = []
        for item_name, prices in self.prices.items():
            try:
                lowest_buy = min([float(price) for price in prices["Buy"].keys()])
                lowest_buy_locations = prices["Buy"][str(lowest_buy)]   # type: list
                if start_locations:
                    lowest_buy_locations = self._get_filtered_locations(start_locations, lowest_buy_locations)
                highest_sell = max([float(price) for price in prices["Sell"].keys()])
                highest_sell_locations = prices["Sell"][str(highest_sell)]
            except KeyError:
                self.logger.warning("Missing prices for '%s'." % item_name)
                continue

            if exclude:
                self._exclude_locations(lowest_buy_locations, highest_sell_locations, exclude)

            if len(lowest_buy_locations) < 1 or len(highest_sell_locations) < 1:
                continue

            bought_units = full_bay * 100
            spent_money = bought_units * lowest_buy
            if spent_money > budget:
                bought_units = budget / lowest_buy
                spent_money = budget

            money_after_trade = bought_units * highest_sell
            routes.append({
                'commodity': item_name,
                'invested money': spent_money,
                'income': round(money_after_trade - spent_money, 2),
                'bought units': round(bought_units, 2),
                'buy locations': ", ".join(["%s (%s)" % (location, self.locations[location])
                                            for location in lowest_buy_locations]),
                'buy price': lowest_buy,
                'sell locations': ", ".join(["%s (%s)" % (location, self.locations[location])
                                            for location in highest_sell_locations]),
                'sell price': highest_sell,
            })
        routes.sort(key=lambda item: item.get('income'), reverse=True)
        return routes[:number_of_routes]
