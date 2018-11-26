
class DataItem(dict):
    def __init__(self, item, parents=None, locations=None, prices=None):
        super().__init__(item)
        self._prices = self._get_prices(prices)
        self._locations = locations
        self._parents = self._get_parents(parents)

    @property
    def id(self):
        return self.get('id')

    def _get_parents(self, all_parents):
        return []

    def _get_prices(self, all_prices):
        return {}


class Commodity(DataItem):

    def _get_prices(self, all_prices):
        prices = {'buy': [], 'sell':[]}
        for price in all_prices.values():
            if price.commodity_id == self.id:
                prices[price.type].append(price)
        return prices

    @property
    def name(self):
        return self.get('commodity_name')

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

    def get_routes_table(self, money=50000, cargo=576, start_location=None, end_location=None, avoid=()):
        routes_data = []
        for buy, sell in self.iterate_filtered_routes(start_location, end_location, avoid):
            bought_units = cargo * 100
            spent_money = bought_units * buy.value
            if spent_money > money:
                bought_units = int(money / buy.value)
                spent_money = money

            routes_data.append({
                'commodity': self.name,
                'invested money': spent_money,
                'income': round((sell.value * bought_units) - spent_money, 2),
                'bought units': round(bought_units, 2),
                'buy price': buy.value,
                'buy location': buy.location.full_string,
                'sell price': sell.value,
                'sell location': sell.location.full_string
            })
        return routes_data


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


class Container(DataItem):

    @property
    def name(self):
        return self.get('container_name')


class Location(DataItem):

    def _get_parent(self, all_parents):
        item_parent_id = self.get('location_container')
        return all_parents.get(item_parent_id)

    def _get_parents(self, all_parents):
        parents = []
        parent = self._get_parent(all_parents)
        while parent:
            parents.append(parent)
            parent_id = parent.get('container_parent')
            parent = all_parents.get(parent_id)
        return parents

    @property
    def name(self):
        return self.get('location_name')

    @property
    def parent(self):
        return self._parents[0]

    @property
    def planet(self):
        try:
            return self._parents[-2]
        except IndexError:
            return None

    @property
    def system(self):
        return self._parents[-1]

    @property
    def parents_string(self):
        return " , ".join([parent.name for parent in self._parents])

    @property
    def full_string(self):
        return "%s @ %s" % (self.name, self.parents_string)


def choose_item_class(items):
    item_keys = items[0].keys()
    if "commodity_name" in item_keys:
        return Commodity
    elif "location_name" in item_keys:
        return Location
    elif "container_name" in item_keys:
        return Container
    elif "price_commodity" in item_keys:
        return CommodityPrice


class DataStructure(dict):
    def __init__(self, items_list, **kwargs):
        item_class = choose_item_class(items_list)
        super().__init__({item['id']: item_class(item, **kwargs) for item in items_list})

    def match_exact_name(self, query):
        for item in self.values():
            if query.lower() == item.name.lower():
                return item

    def match_names(self, query):
        return [item.id for item in self.values() if query.lower() in item.name.lower()]

    def exclude_names(self, query):
        return [item.id for item in self.values() if query.lower() not in item.name.lower()]

    def match_and_exclude_names(self, match_query, exclude_query):
        return [item.id for item in self.values()
                if match_query.lower() in item.name.lower() and exclude_query.lower() not in item.name.lower()]

    def auto_match_names(self, match_query, exclude_query):
        if match_query and exclude_query:
            return self.match_and_exclude_names(match_query, exclude_query)
        elif match_query:
            return self.match_names(match_query)
        elif exclude_query:
            return self.exclude_names(exclude_query)
