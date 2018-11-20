
class DataItem(dict):
    def __init__(self, item, parents=None, commodities=None, locations=None):
        super().__init__(item)
        self._parents = parents
        self._commodities = commodities
        self._locations = locations


class Commodity(DataItem):

    @property
    def name(self):
        return self.get('commodity_name')


class CommodityPrice(DataItem):

    @property
    def commodity(self):
        commodity_id = self.get('price_commodity')
        return self._commodities.get(commodity_id)

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

    @property
    def name(self):
        return self.get('location_name')

    @property
    def parent(self):
        item_parent_id = self.get('location_container')
        return self._parents.get(item_parent_id)

    @property
    def parents_string(self):
        parents_names = []
        parent = self.parent
        while parent:
            parents_names.append(parent.name)
            parent_id = parent.get('container_parent')
            parent = self._parents.get(parent_id)
        return " , ".join(parents_names)


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
        return [item['id'] for item in self.values() if query.lower() in item.name.lower()]

    def exclude_names(self, query):
        return [item['id'] for item in self.values() if query.lower() not in item.name.lower()]

    def match_and_exclude_names(self, match_query, exclude_query):
        return [item['id'] for item in self.values()
                if match_query.lower() in item.name.lower() and exclude_query.lower() not in item.name.lower()]

    def auto_match_names(self, match_query, exclude_query):
        if match_query and exclude_query:
            return self.match_and_exclude_names(match_query, exclude_query)
        elif match_query:
            return self.match_names(match_query)
        elif exclude_query:
            return self.exclude_names(exclude_query)
