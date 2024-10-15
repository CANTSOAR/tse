class Participant():

    def __init__(self, name, cash = 1000, position_limits = 10):
        self.__name = name
        self.__cash = cash
        self.__open_orders = {}
        self.__open_positions = {}
        self.__position_limits = position_limits
        self.__current_position_size = {}
    
    def update_positions(self, orderbook, asset, position_update, cash_change):
        from orderbook import Orderbook
        if not isinstance(orderbook, Orderbook):
            return

        self.__cash += cash_change

        if asset in self.__open_positions:
            self.__open_positions[asset] += position_update
        else:
            self.__open_positions[asset] = position_update

    def get_name(self):
        return self.__name

    def get_cash(self):
        return self.__cash

    def get_open_orders(self):
        return self.__open_orders

    def get_open_positions(self):
        return self.__open_positions

    def get_position_limits(self):
        return self.__position_limits

    def get_current_position_size(self):
        return self.__current_position_size