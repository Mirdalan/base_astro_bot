from .data_classes import DataItem


class Commodity(DataItem):

    def _get_prices(self, all_prices):
        prices = {'buy': [], 'sell': []}
        for price in all_prices.values():
            if price.commodity_id == self.id:
                prices[price.type].append(price)
        return prices

    @property
    def name(self):
        return self.get('commodity_name')

    @property
    def illegal(self):
        return self.get('commodity_illegal')

    @property
    def legal(self):
        return not self.illegal

    @property
    def buy_prices(self):
        return self._prices['buy']

    @property
    def best_buy(self):
        return min(price.value for price in self.buy_prices)

    @property
    def sell_prices(self):
        return self._prices['sell']

    @property
    def best_sell(self):
        return max(price.value for price in self.buy_prices)

    @property
    def best_deal(self):
        return self.best_sell - self.best_buy

    def iterate_all_routes(self):
        for buy in self.buy_prices:
            for sell in self.sell_prices:
                yield buy, sell

    def iterate_filtered_routes(self, start_location=None, end_location=None, avoid=()):

        def location_matches_query(price, start_end_query):
            return not start_end_query or start_end_query.lower() in price.location.full_string.lower()

        def not_avoiding_location(price):
            return all(avoid_location.lower() not in price.location.full_string.lower() for avoid_location in avoid)

        def location_matches_conditions(price, query):
            return location_matches_query(price, query) and not_avoiding_location(price)

        for buy, sell in self.iterate_all_routes():   # type: CommodityPrice, CommodityPrice
            if location_matches_conditions(buy, start_location) and location_matches_conditions(sell, end_location):
                yield buy, sell

    def get_routes(self, cargo=576, money=50000, start_location=None, end_location=None, avoid=()):
        routes_data = []
        best_income = 0.0
        for buy, sell in self.iterate_filtered_routes(start_location, end_location, avoid):
            bought_units = cargo * 100
            spent_money = bought_units * buy.value
            if spent_money > money:
                bought_units = int(money / buy.value)
                spent_money = money

            income = round((sell.value * bought_units) - spent_money, 2)
            if income > best_income:
                best_income = income

            routes_data.append({
                'commodity': self.name,
                'invested money': spent_money,
                'income': income,
                'bought units': round(bought_units, 2),
                'buy price': buy.value,
                'buy location': buy.location.full_string,
                'sell price': sell.value,
                'sell location': sell.location.full_string
            })
        routes_data.sort(key=lambda item: item.get('income'), reverse=True)
        return {
            "best_income": best_income,
            "routes": routes_data
        }


class CommodityPrice(DataItem):

    @property
    def commodity_id(self):
        return self.get('price_commodity')

    @property
    def location(self):
        location_id = self.get('price_location')
        return self._locations.get(location_id)

    @property
    def type(self):
        return self.get('price_type')

    @property
    def value(self):
        return self.get('price_unit_price')
