from participant import Participant
from order import Order
import random

class bBot1(Participant):

    def __init__(self, name, bid, ask, order_size, asset_name):
        super().__init__(name)        
        self.bid = bid
        self.ask = ask
        self.order_size = order_size
        self.asset_name = asset_name

    def evaluate_tick(self, order_book_data):
        order1 = Order(self.asset_name, self.bid + int(10 * random.random()) - 5, self.order_size + int(10 * random.random()) - 5, self)
        order2 = Order(self.asset_name, -self.ask + int(10 * random.random()) - 5, self.order_size + int(10 * random.random()) - 5, self)

        return [order1, order2] #must return an array of orders