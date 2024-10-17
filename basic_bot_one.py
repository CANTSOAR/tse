from participant import Participant
from order import Order
import random

class Algo(Participant):

    def __init__(self):
        super().__init__("Basic Bot #1", position_limits = 1000)

    def evaluate_tick(self, order_book_data):
        return [Order("oranges", 48 + int(10 * random.random()) - 5, 100 + int(10 * random.random()) - 5)]