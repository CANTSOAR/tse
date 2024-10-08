import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.animation import FuncAnimation
import time
import copy
from order import Order
from participant import Participant


class Orderbook():

    mkt_participants: list[Participant] = []
    all_participant_history = []
    mkt_assets = []

    order_cache: list[Order] = []
    order_history = []

    order_book = {}
    priv_order_book = {}
    all_book_history = []

    position_cache = {}

    tick_rate = 0 #0 is asap, and others are in ticks per second
    ticks_from_start = 0
    

    def __init__(self, mkt_participants, tick_rate = 0):
        self.mkt_participants = mkt_participants
        self.tick_rate = tick_rate

    def compute_next_tick(self):
        participant_data = {}

        for participant in self.mkt_participants:
            try:
                incoming_orders = participant.evaluate_tick(self.order_book)
            except:
                incoming_orders = []

            self.order_cache += incoming_orders

            participant_data[participant._name] = [participant.cash, participant._open_orders, participant._open_positions]

        self.all_participant_history.append(participant_data)

    def evaluate_tick(self):
        for asset in self.order_book:
            asset_prices = np.array(list(self.order_book[asset].keys()))

            try:
                highest_bid = np.max(asset_prices)
                lowest_ask = np.max(asset_prices[asset_prices < 0])
            except:
                continue

            while highest_bid >= -lowest_ask:
                volume_traded = min(self.order_book[asset][highest_bid], self.order_book[asset][lowest_ask])
                leftover = self.order_book[asset][highest_bid] - self.order_book[asset][lowest_ask]
                
                bid_ticks = self.priv_order_book[asset][highest_bid]["tick"][:volume_traded]
                ask_ticks = self.priv_order_book[asset][lowest_ask]["tick"][:volume_traded]

                prices = highest_bid * (bid_ticks < ask_ticks) + -lowest_ask * (bid_ticks > ask_ticks) + (highest_bid - lowest_ask) / 2 * (bid_ticks == ask_ticks)

                buyer_changes = np.arange(volume_traded)[np.concatenate(([True], self.priv_order_book[asset][highest_bid]["id"][:volume_traded - 1] != self.priv_order_book[asset][highest_bid]["id"][1:volume_traded]))]
                seller_changes = np.arange(volume_traded)[np.concatenate(([True], self.priv_order_book[asset][lowest_ask]["id"][:volume_traded - 1] != self.priv_order_book[asset][lowest_ask]["id"][1:volume_traded]))]

                buyer_position_sizes = np.arange(volume_traded)[np.concatenate((self.priv_order_book[asset][highest_bid]["id"][:volume_traded - 1] != self.priv_order_book[asset][highest_bid]["id"][1:volume_traded], [True]))]\
                     - buyer_changes + 1
                seller_position_sizes = np.arange(volume_traded)[np.concatenate((self.priv_order_book[asset][lowest_ask]["id"][:volume_traded - 1] != self.priv_order_book[asset][lowest_ask]["id"][1:volume_traded], [True]))]\
                     - seller_changes + 1

                buyer_freqs = np.column_stack((
                    self.priv_order_book[asset][highest_bid]["owner"][:volume_traded][buyer_changes],
                    self.priv_order_book[asset][highest_bid]["id"][:volume_traded][buyer_changes],
                    buyer_position_sizes,
                    -prices[buyer_changes]))
                seller_freqs = np.column_stack((
                    self.priv_order_book[asset][lowest_ask]["owner"][:volume_traded][seller_changes],
                    self.priv_order_book[asset][lowest_ask]["id"][:volume_traded][seller_changes],
                    -seller_position_sizes,
                    prices[seller_changes]))

                if leftover > 0:
                    self.order_book[asset][highest_bid] -= volume_traded
                    self.priv_order_book[asset][highest_bid]["owner"] = self.priv_order_book[asset][highest_bid]["owner"][volume_traded:]
                    self.priv_order_book[asset][highest_bid]["tick"] = self.priv_order_book[asset][highest_bid]["tick"][volume_traded:]
                    self.priv_order_book[asset][highest_bid]["id"] = self.priv_order_book[asset][highest_bid]["id"][volume_traded:]

                    del self.order_book[asset][lowest_ask]
                    del self.priv_order_book[asset][lowest_ask]

                elif leftover < 0:
                    self.order_book[asset][lowest_ask] -= volume_traded
                    self.priv_order_book[asset][lowest_ask]["owner"] = self.priv_order_book[asset][lowest_ask]["owner"][volume_traded:]
                    self.priv_order_book[asset][lowest_ask]["tick"] = self.priv_order_book[asset][lowest_ask]["tick"][volume_traded:]
                    self.priv_order_book[asset][lowest_ask]["id"] = self.priv_order_book[asset][lowest_ask]["id"][volume_traded:]

                    del self.order_book[asset][highest_bid]
                    del self.priv_order_book[asset][highest_bid]

                else:
                    del self.order_book[asset][highest_bid]
                    del self.priv_order_book[asset][highest_bid]
                    del self.order_book[asset][lowest_ask]
                    del self.priv_order_book[asset][lowest_ask]

                if asset in self.position_cache:
                   self.position_cache[asset] += np.concatenate((buyer_freqs, seller_freqs)).tolist()
                else:
                   self.position_cache[asset] = np.concatenate((buyer_freqs, seller_freqs)).tolist()
                
                try:
                    asset_prices = np.array(list(self.order_book[asset].keys()))
                    highest_bid = np.max((asset_prices))
                    lowest_ask = np.max((asset_prices[asset_prices < 0]))
                except:
                    break


    def update_order_book(self):
        for order in self.order_cache:
            self.order_history.append(order)

            if order.asset not in self.mkt_assets: self.mkt_assets.append(order.asset)

            if order.asset in self.order_book:
                if order.price in self.order_book[order.asset]:
                    self.order_book[order.asset][order.price] += order.size
                    self.priv_order_book[order.asset][order.price]["owner"] = np.concatenate((self.priv_order_book[order.asset][order.price]["owner"], [self.mkt_participants.index(order.owner)] * order.size))
                    self.priv_order_book[order.asset][order.price]["tick"] = np.concatenate((self.priv_order_book[order.asset][order.price]["tick"], [self.ticks_from_start] * order.size))
                    self.priv_order_book[order.asset][order.price]["id"] = np.concatenate((self.priv_order_book[order.asset][order.price]["id"], [self.order_history.index(order)] * order.size))
                else:
                    self.order_book[order.asset][order.price] = order.size
                    self.priv_order_book[order.asset][order.price] = {}

                    self.priv_order_book[order.asset][order.price]["owner"] = np.array([self.mkt_participants.index(order.owner)] * order.size)
                    self.priv_order_book[order.asset][order.price]["tick"] = np.array([self.ticks_from_start] * order.size)
                    self.priv_order_book[order.asset][order.price]["id"] = np.array([self.order_history.index(order)] * order.size)
            else:
                self.order_book[order.asset] = {order.price: order.size}
                self.priv_order_book[order.asset] = {order.price: {}}

                self.priv_order_book[order.asset][order.price]["owner"] = np.array([self.mkt_participants.index(order.owner)] * order.size)
                self.priv_order_book[order.asset][order.price]["tick"] = np.array([self.ticks_from_start] * order.size)
                self.priv_order_book[order.asset][order.price]["id"] = np.array([self.order_history.index(order)] * order.size)

            order.owner._open_orders[self.order_history.index(order)] = order

        self.order_cache = []

    def update_positions(self):
        for asset in self.position_cache:
            for owner, id, position_update, cash_update in self.position_cache[asset]:
                self.mkt_participants[int(owner)]._update_positions(asset, position_update, cash_update)
                self.mkt_participants[int(owner)]._open_orders[int(id)].update_size(-abs(position_update), int(id))

        self.position_cache = {}

    def main_loop(self, ticks_to_run = float("inf")):
        while ticks_to_run > 0:
            self.compute_next_tick()    #inbound orders
            self.update_order_book()    #populate orderbook

            self.all_book_history.append(copy.deepcopy(self.priv_order_book)) #keep current book state for recording

            self.evaluate_tick()        #make a market
            self.update_positions()     #update portfolios

            self.ticks_from_start += 1
            ticks_to_run -= 1
            if self.tick_rate: time.sleep(1 / self.tick_rate())

    def visualize(self):
        order_size_cmap = LinearSegmentedColormap.from_list("order_size_cmap", [(0, "#00ff08"), 
                                                                                (.5, "#1fcc00"),
                                                                                (.5, "#9c0000"), 
                                                                                (1, "#ff0000")])
        
        for asset in self.mkt_assets:
            for timestamp in range(len(self.all_book_history)):
                order_sizes = np.array([abs(price) / (price + .0001) * len(orders["owner"]) for price, orders in self.all_book_history[timestamp][asset].items()])
                order_size_colors = (order_sizes / max((abs(order_sizes))) + 1) / 2
                order_size_alphas = abs(order_sizes) / max((abs(order_sizes))) / 4 * 3 + .25
                
                plt.scatter([timestamp] * len(self.all_book_history[timestamp][asset]), np.abs(list(self.all_book_history[timestamp][asset].keys())), c = order_size_colors, cmap = order_size_cmap, alpha = order_size_alphas, marker = "s", norm = Normalize(0, 1, True))

            plt.title(asset)
            plt.xlabel("Ticks")
            plt.ylabel("Price")
            plt.show()

    def animate(self):
        order_size_cmap = LinearSegmentedColormap.from_list("order_size_cmap", [(0, "#00ff08"), 
                                                                                (.5, "#1fcc00"), 
                                                                                (.5, "#9c0000"), 
                                                                                (1, "#ff0000")])
        
        for asset in self.mkt_assets:
            tick_data = []
            tick_data_size = []

            for timestamp in range(len(self.all_book_history)):
                order_sizes = np.array([abs(price) / (price + .0001) * len(orders["owner"]) for price, orders in self.all_book_history[timestamp][asset].items()])
                order_size_colors = (order_sizes / max((abs(order_sizes))) + 1) / 2
                order_size_alphas = abs(order_sizes) / max((abs(order_sizes))) / 4 * 3 + .25
                
                tick_data.append([[timestamp] * len(self.all_book_history[timestamp][asset]), np.abs(list(self.all_book_history[timestamp][asset].keys())), order_size_colors, order_size_alphas])
                tick_data_size.append(len(self.all_book_history[timestamp][asset]))

            tick_data = np.concatenate(tick_data, axis = 1)
            tick_data_size = np.cumsum(tick_data_size)

            fig = plt.figure()
            ax = plt.axes(xlim=(0, len(self.all_book_history)), ylim=(np.min(tick_data[1]), np.max(tick_data[1])))
            scatter = ax.scatter([], [], c = [], cmap = order_size_cmap, marker = "s", norm = Normalize(0, 1, True))

            def update(i):
                x = tick_data[0][:tick_data_size[i]]
                y = tick_data[1][:tick_data_size[i]]
                c = tick_data[2][:tick_data_size[i]]
                a = tick_data[3][:tick_data_size[i]]

                data = np.column_stack((x, y))

                scatter.set_offsets(data)
                scatter.set_array(c)
                scatter.set_alpha(a)

                return scatter,
            
            ani = FuncAnimation(fig, update, frames = range(len(self.all_book_history)), interval = 100, blit = True, repeat = False)

            plt.title(asset)
            plt.xlabel("Ticks")
            plt.ylabel("Price")
            plt.show()