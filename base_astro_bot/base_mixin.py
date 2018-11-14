

class BaseMixinClass:
    logger = None
    messages = None
    rsi_data = None
    database_manager = None
    max_ships = None
    ship_data_headers = None

    @staticmethod
    def mention_user(user):
        raise NotImplementedError

    def get_author_if_given(self, author):
        raise NotImplementedError

    @staticmethod
    def print_dict_table(*args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def print_list_table(*args, **kwargs):
        raise NotImplementedError

    def split_data_and_get_messages(self, *args, **kwargs):
        raise NotImplementedError
