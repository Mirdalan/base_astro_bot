
class TableDict(dict):
    pass


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
        return ", ".join([parent.name for parent in self._parents])

    @property
    def short_string(self):
        return "%s @ %s" % (self.name, self.parent.name)

    @property
    def full_string(self):
        return "%s @ %s" % (self.name, self.parents_string)
