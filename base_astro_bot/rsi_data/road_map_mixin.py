from abc import ABC

from tabulate import tabulate

from ..base_mixin import BaseMixinClass


class RoadMapMixin(BaseMixinClass, ABC):

    def get_no_road_map_data_found_message(self):
            self.logger.debug("No Roadmap data found...")
            return self.messages.road_map_not_found % tabulate(self.rsi_data.road_map.get_releases_and_categories(),
                                                               tablefmt="fancy_grid")

    @staticmethod
    def _data_found(data, find):
        return (not find) or (find.lower() in data.lower())

    @staticmethod
    def _get_road_map_table(value, key):
        return "```\n%s\n```" % tabulate(value, tablefmt="presto", headers=(key, "Task", "Done"))

    def _get_road_map_data_message(self, data, find=None):
        result = []
        if data:
            self.logger.debug("Showing Roadmap...")
            if isinstance(data, str):
                if self._data_found(data, find):
                    result = [self.print_dict_table(data, table_format="fancy_grid")]
            elif isinstance(data, dict):
                for key, value in data.items():
                    if self._data_found(key + str(value), find):
                        result += self.split_data_and_get_messages(value, self._get_road_map_table, key)
        if result:
            return result
        else:
            return [self.get_no_road_map_data_found_message()]

    def get_road_map_messages(self, args):
        self.logger.debug("Requested Roadmap.")
        if args.category and args.version:
            result = self.rsi_data.road_map.get_release_category_details(args.version, args.category)
            result = self._get_road_map_data_message(result)
        elif args.version:
            result = self.rsi_data.road_map.get_release_details(args.version)
            result = self._get_road_map_data_message(result, find=args.find)
        elif args.category:
            result = self.rsi_data.road_map.get_category_details(args.category)
            result = self._get_road_map_data_message(result, find=args.find)
        elif args.list:
            result = self.rsi_data.road_map.get_releases_and_categories()
            result = [self.print_dict_table(result, table_format="fancy_grid")]
        elif args.find:
            result = self.rsi_data.road_map.get()
            result = self._get_road_map_data_message(result, find=args.find)
        elif args.update:
            result = self.rsi_data.road_map.update_data()
            result = [self.messages.success] if result else [self.messages.something_went_wrong]
        else:
            result = self.rsi_data.road_map.get_releases()
            result = [self.print_dict_table(result, table_format="fancy_grid")]
        return result
