from . import data_classes
from . import trade_classes


def choose_item_class(items):
    item_keys = items[0].keys()
    if "location_name" in item_keys:
        return data_classes.Location
    elif "container_name" in item_keys:
        return data_classes.Container
    elif "commodity_name" in item_keys:
        return trade_classes.Commodity
    elif "price_commodity" in item_keys:
        return trade_classes.CommodityPrice
    elif "resource_name" in item_keys:
        return trade_classes.Resource
    elif "price_resource" in item_keys:
        return trade_classes.ResourcePrice


class DataStructure(dict):
    def __init__(self, items_list, **kwargs):
        item_class = choose_item_class(items_list)
        super().__init__({item['id']: item_class(item, **kwargs) for item in items_list})

    def get_list(self):
        return list(self.values())

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
