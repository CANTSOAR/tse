from participant import Participant
from order import Order
import random

class bBot1(Participant):

    def __init__(self, name, bid, ask, bid_order_size, ask_order_size, asset_name):
        super().__init__(name)        
        self.bid = bid
        self.ask = ask
        self.bid_order_size = bid_order_size
        self.ask_order_size = ask_order_size
        self.asset_name = asset_name
        self._position_limits = 10000

    def evaluate_tick(self, order_book_data):
        orders = []
        if self.bid_order_size: orders.append(Order(self.asset_name, self.bid + int(10 * random.random()) - 5, self.bid_order_size + int(10 * random.random()) - 5, self))
        if self.ask_order_size: orders.append(Order(self.asset_name, self.ask + int(10 * random.random()) - 5, -self.ask_order_size + int(10 * random.random()) - 5, self))

        return orders #must return an array of orders