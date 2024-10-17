from participant import Participant #NEEDED TO RUN
from order import Order             #NEEDED TO RUN
import numpy as np

class Algo(Participant):

    #DO NOT TOUCH
    def __init__(self):
        super().__init__("sample")

    #example of a basic market taking strategy (probably wont make money)
    def evaluate_tick(self, order_book_data):
        oranges_expected_midline = 50
        kiwis_expected_midline = 155

        tolerance = 2

        orders = []

        if order_book_data:
            oranges = order_book_data["oranges"]
            kiwis = order_book_data["green kiwis"]

            orange_bids = np.array(list(oranges["bids"].keys()))
            orange_asks = np.array(list(oranges["asks"].keys()))
            
            kiwi_bids = np.array(list(kiwis["bids"].keys()))
            kiwi_asks = np.array(list(kiwis["asks"].keys()))

            if max(orange_bids) > oranges_expected_midline - tolerance:
                #print("long orange", min(oranges["bids"][max(orange_bids)], self.get_position_limits() - self.get_current_position_size()["oranges"]), oranges_expected_midline - tolerance)
                ask_order = Order("oranges",oranges_expected_midline - tolerance, -min(oranges["bids"][max(orange_bids)], self.get_position_limits() - self.get_current_position_size()["oranges"]))
                orders.append(ask_order)
            if min(orange_asks) < oranges_expected_midline + tolerance:
                #print("short orange", max(oranges["asks"][min(orange_asks)], -self.get_position_limits() - self.get_current_position_size()["oranges"]), oranges_expected_midline + tolerance)
                bid_order = Order("oranges", oranges_expected_midline + tolerance, min(oranges["asks"][min(orange_asks)], self.get_position_limits() - self.get_current_position_size()["oranges"]))
                orders.append(bid_order)

            if max(kiwi_bids) > kiwis_expected_midline - tolerance:
                #print("long kiwi", min(kiwis["bids"][max(kiwi_bids)], self.get_position_limits() - self.get_current_position_size()["green kiwis"]), kiwis_expected_midline - tolerance)
                ask_order = Order("green kiwis", kiwis_expected_midline - tolerance, -min(kiwis["bids"][max(kiwi_bids)], self.get_position_limits() - self.get_current_position_size()["green kiwis"]))
                orders.append(ask_order)
            if min(kiwi_asks) < kiwis_expected_midline + tolerance:
                #print("short kiwi", max(kiwis["asks"][min(kiwi_asks)], -self.get_position_limits() - self.get_current_position_size()["green kiwis"]), kiwis_expected_midline + tolerance)
                bid_order = Order("green kiwis", kiwis_expected_midline + tolerance, min(kiwis["asks"][min(kiwi_asks)], self.get_position_limits() - self.get_current_position_size()["green kiwis"]))
                orders.append(bid_order)


        return orders #must return an array of orders