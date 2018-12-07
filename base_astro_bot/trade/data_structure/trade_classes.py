from .data_classes import Item, Price


class Commodity(Item):
    name_prefix = "commodity"

    @property
    def illegal(self):
        return self.get('%s_illegal' % self.name_prefix)

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
            return price.location and location_matches_query(price, query) and not_avoiding_location(price)

        for buy, sell in self.iterate_all_routes():   # type: CommodityPrice, CommodityPrice
            if location_matches_conditions(buy, start_location) and location_matches_conditions(sell, end_location):
                yield buy, sell

    def get_routes(self, cargo=576, money=50000, start_location=None, end_location=None, avoid=(), max_routes=3):

        def duplicate_value_route():
            for item in routes_data:
                if buy.value == item['buy price'] and sell.value == item['sell price']:
                    if buy.location.short_string not in item['buy locations']:
                        item['buy locations'] += "\n%s" % buy.location.short_string
                    if sell.location.short_string not in item['sell locations']:
                        item['sell locations'] += "\n%s" % sell.location.short_string
                    return True

        routes_data = []
        best_income = 0.0
        for buy, sell in self.iterate_filtered_routes(start_location, end_location, avoid):

            if duplicate_value_route():
                continue

            bought_units = cargo * 100
            spent_money = bought_units * buy.value
            if spent_money > money:
                bought_units = int(money / buy.value)
                spent_money = money

            income = round((sell.value * bought_units) - spent_money, 2)
            if income > best_income:
                best_income = income

            routes_data.append({
                'invested money': spent_money,
                'income': income,
                'bought units': round(bought_units, 2),
                'buy price': buy.value,
                'buy locations': buy.location.short_string,
                'sell price': sell.value,
                'sell locations': sell.location.short_string
            })
        if routes_data:
            routes_data.sort(key=lambda item: item.get('income'), reverse=True)
            routes_data = routes_data[:max_routes]
            table = [[key] + [item[key] for item in routes_data] for key in routes_data[0].keys()]

            return {
                '%s_name' % self.name_prefix: self.name,
                'best_income': best_income,
                'routes': routes_data,
                'table': table
            }


class Resource(Item):
    name_prefix = "resource"

    @property
    def type(self):
        return self.get('resource_type')

    def get_prices_table(self):
        return [{
            'aUEC/unit': price.value,
            'Locations': price.location.short_string
        } for price in self.sell_prices]


class CommodityPrice(Price):
    name_suffix = "commodity"


class ResourcePrice(Price):
    name_suffix = "resource"
