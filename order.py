class Order():

    def __init__(self, asset, price, size):
        self.__asset: str = asset
        self.__price: float = price
        self.__size: int = size
        self.__owner = None

    def update_size(self, caller, update, id):
        from orderbook import Orderbook
        if not isinstance(caller, Orderbook):
            return
        
        self.__size += update
        if not self.__size:
            self.__owner.update_open_orders(self, -id, self)
            del self

    def cancel_order(self, caller):
        from orderbook import Orderbook
        if not isinstance(caller, Orderbook) and caller != self.__owner:
            return
        
        del self

    def set_owner(self, caller, owner):
        from orderbook import Orderbook
        if not isinstance(caller, Orderbook):
            return
        
        self.__owner = owner

    def get_asset(self):
        return self.__asset

    def get_price(self):
        return self.__price

    def get_size(self):
        return self.__size

    def get_owner(self):
        return self.__owner
