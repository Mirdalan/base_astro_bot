
class DataItem(dict):
    def __init__(self, item, parents=None, locations=None, prices=None):
        super().__init__(item)
        self._prices = self._get_prices(prices)
        self._locations = locations
        self._parents = self._get_parents(parents)
        self._best_sell = self._get_best_sell()

    @property
    def id(self):
        return self.get('id')

    def _get_parents(self, all_parents):
        return []

    def _get_prices(self, all_prices):
        return {}

    def _get_best_sell(self):
        return None


class Item(DataItem):
    name_prefix = ""

    def _get_prices(self, all_prices):
        prices = {'buy': [], 'sell': []}
        for price in all_prices.values():
            if price.commodity_id == self.id:
                prices[price.type].append(price)
        return prices

    @property
    def name(self):
        return self.get('%s_name' % self.name_prefix)

    @property
    def sell_prices(self):
        return self._prices['sell']

    def _get_best_sell(self):
        if self.sell_prices:
            return max(price.value for price in self.sell_prices)

    @property
    def best_sell(self):
        return self._best_sell

    @property
    def best_sell_locations(self):
        return [price.location.short_name for price in self.sell_prices if price.value == self.best_sell]


class Price(DataItem):
    name_suffix = ""

    @property
    def commodity_id(self):
        return self.get('price_%s' % self.name_suffix)

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
    def short_name(self):
        short_name = self.name.replace("Mining", "M.").replace("Research", "R.")
        short_name = short_name.replace(" Area", "A.").replace(" Outpost", "O.").replace(" Facility", "F.")
        if len(short_name) > 20:
            short_name = short_name[:20]
        return short_name

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
        return ", ".join([parent.name for parent in self._parents])

    @property
    def short_string(self):
        return "%s @ %s" % (self.short_name, self.parent.name)

    @property
    def full_string(self):
        return "%s @ %s" % (self.name, self.parents_string)
