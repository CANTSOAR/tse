class Participant():

    def __init__(self, name, cash = 1000, position_limits = 10):
        self.__name = name
        self.__cash = cash
        self.__open_orders = {}
        self.__open_positions = {}
        self.__position_limits = position_limits
    
    def update_open_positions(self, orderbook, asset, position_update, cash_change):
        from orderbook import Orderbook
        if not isinstance(orderbook, Orderbook):
            return

        self.__cash += cash_change

        if asset in self.__open_positions:
            self.__open_positions[asset] += position_update
        else:
            self.__open_positions[asset] = position_update

    def update_open_orders(self, caller, order_id, order):
        from orderbook import Orderbook
        from order import Order
        if not isinstance(caller, Orderbook) and not isinstance(caller, Order):
            return
        
        if order_id > 0: self.__open_orders[abs(order_id)] = order
        else: del self.__open_orders[abs(order_id)]

    def clean(self, caller):
        from orderbook import Orderbook
        if not isinstance(caller, Orderbook):
            return
        
        self.__open_orders.clear()
        self.__open_positions.clear()

    def get_name(self):
        return self.__name

    def get_cash(self):
        return self.__cash

    def get_open_orders(self):
        return self.__open_orders.copy()

    def get_open_positions(self):
        return self.__open_positions.copy()

    def get_position_limits(self):
        return self.__position_limits