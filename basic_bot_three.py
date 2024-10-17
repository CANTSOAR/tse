from participant import Participant
from order import Order
import random

class Algo(Participant):

    def __init__(self):
        super().__init__("Basic Bot #3", position_limits = 1000)

    def evaluate_tick(self, order_book_data):
        orders = [
            Order("green kiwis", 154 + int(10 * random.random()) - 5, 1000 + int(10 * random.random()) - 5),
            Order("green kiwis", 158 + int(10 * random.random()) - 5, -1000 + int(10 * random.random()) - 5)
                  ]
        return orders