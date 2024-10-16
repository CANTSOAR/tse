from participant import Participant
from order import Order
import random

class Algo(Participant):

    def __init__(self):
        super().__init__("Basic Bot #4", position_limits = 1000)

    def evaluate_tick(self, order_book_data):
        orders = [
            Order("green kiwis", 150 + int(10 * random.random()) - 5, 1000 + int(10 * random.random()) - 5, self),
            Order("green kiwis", 156 + int(10 * random.random()) - 5, -1000 + int(10 * random.random()) - 5, self)
                  ]
        return orders