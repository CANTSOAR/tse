import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.animation import FuncAnimation
import time
import copy
from order import Order
from participant import Participant


class Orderbook():

    def __init__(self, mkt_participants, tick_rate = 0):
        self.__mkt_participants: list[Participant] = mkt_participants
        self.__all_participant_history = []
        self.__mkt_assets = []
        self.__mkt_assets_ltp = {}

        self.__order_cache: list[Order] = []
        self.__order_history: list[Order] = []

        self.__order_book = {}
        self.__priv_order_book = {}
        self.__all_book_history = []

        self.__position_cache = {}

        self.__tick_rate = tick_rate #0 is asap, and others are in ticks per second
        self.__ticks_from_start = 0
        print("i love my girlfriend, she is amazing")

    def __compute_next_tick(self):
        participant_data = {}

        for participant in self.__mkt_participants:
            try:
                incoming_orders: list[Order] = participant.evaluate_tick(self.__order_book)
            except:
                incoming_orders = []

            for order in incoming_orders:
                order.set_owner(self, participant)

            self.__order_cache += incoming_orders

            participant_data[participant.get_name()] = [participant.get_cash(), participant.get_open_orders(), participant.get_open_positions()]

        self.__all_participant_history.append(participant_data)

    def __evaluate_tick(self):
        for asset in self.__order_book:
            asset_bid_prices = np.array(list(self.__order_book[asset]["bids"].keys()))
            asset_ask_prices = np.array(list(self.__order_book[asset]["asks"].keys()))

            if asset_bid_prices.any(): highest_bid = np.max(asset_bid_prices)
            else: continue
            if asset_ask_prices.any(): lowest_ask = np.min(asset_ask_prices)
            else: continue

            while highest_bid >= lowest_ask:
                volume_traded = min(self.__order_book[asset]["bids"][highest_bid], -self.__order_book[asset]["asks"][lowest_ask])
                leftover = self.__order_book[asset]["bids"][highest_bid] + self.__order_book[asset]["asks"][lowest_ask]

                bid_ticks = self.__priv_order_book[asset]["bids"][highest_bid]["tick"][:volume_traded]
                ask_ticks = self.__priv_order_book[asset]["asks"][lowest_ask]["tick"][:volume_traded]

                prices = highest_bid * (bid_ticks < ask_ticks) + lowest_ask * (bid_ticks > ask_ticks) + (highest_bid + lowest_ask) / 2 * (bid_ticks == ask_ticks)
                self.__mkt_assets_ltp[asset] = prices[np.max([bid_ticks, ask_ticks], axis = 0) == max(max(bid_ticks), max(ask_ticks))][-1]

                buyer_changes = np.arange(volume_traded)[np.concatenate(([True], self.__priv_order_book[asset]["bids"][highest_bid]["id"][:volume_traded - 1] != self.__priv_order_book[asset]["bids"][highest_bid]["id"][1:volume_traded]))]
                seller_changes = np.arange(volume_traded)[np.concatenate(([True], self.__priv_order_book[asset]["asks"][lowest_ask]["id"][:volume_traded - 1] != self.__priv_order_book[asset]["asks"][lowest_ask]["id"][1:volume_traded]))]

                buyer_position_sizes = np.arange(volume_traded)[np.concatenate((self.__priv_order_book[asset]["bids"][highest_bid]["id"][:volume_traded - 1] != self.__priv_order_book[asset]["bids"][highest_bid]["id"][1:volume_traded], [True]))]\
                     - buyer_changes + 1
                seller_position_sizes = np.arange(volume_traded)[np.concatenate((self.__priv_order_book[asset]["asks"][lowest_ask]["id"][:volume_traded - 1] != self.__priv_order_book[asset]["asks"][lowest_ask]["id"][1:volume_traded], [True]))]\
                     - seller_changes + 1

                order_splits = [buyer_changes, seller_changes][int(len(buyer_changes) > len(seller_changes))]
                order_sizes = [buyer_position_sizes, seller_position_sizes][int(len(buyer_position_sizes) > len(seller_position_sizes))]

                buyer_freqs = np.column_stack((
                    self.__priv_order_book[asset]["bids"][highest_bid]["owner"][:volume_traded][order_splits],
                    self.__priv_order_book[asset]["bids"][highest_bid]["id"][:volume_traded][order_splits],
                    order_sizes,
                    -prices[order_splits] * order_sizes))
                seller_freqs = np.column_stack((
                    self.__priv_order_book[asset]["asks"][lowest_ask]["owner"][:volume_traded][order_splits],
                    self.__priv_order_book[asset]["asks"][lowest_ask]["id"][:volume_traded][order_splits],
                    -order_sizes,
                    prices[order_splits] * order_sizes))

                if leftover > 0:
                    self.__order_book[asset]["bids"][highest_bid] -= volume_traded
                    self.__priv_order_book[asset]["bids"][highest_bid]["owner"] = self.__priv_order_book[asset]["bids"][highest_bid]["owner"][volume_traded:]
                    self.__priv_order_book[asset]["bids"][highest_bid]["tick"] = self.__priv_order_book[asset]["bids"][highest_bid]["tick"][volume_traded:]
                    self.__priv_order_book[asset]["bids"][highest_bid]["id"] = self.__priv_order_book[asset]["bids"][highest_bid]["id"][volume_traded:]

                    del self.__order_book[asset]["asks"][lowest_ask]
                    del self.__priv_order_book[asset]["asks"][lowest_ask]

                elif leftover < 0:
                    self.__order_book[asset]["asks"][lowest_ask] += volume_traded
                    self.__priv_order_book[asset]["asks"][lowest_ask]["owner"] = self.__priv_order_book[asset]["asks"][lowest_ask]["owner"][volume_traded:]
                    self.__priv_order_book[asset]["asks"][lowest_ask]["tick"] = self.__priv_order_book[asset]["asks"][lowest_ask]["tick"][volume_traded:]
                    self.__priv_order_book[asset]["asks"][lowest_ask]["id"] = self.__priv_order_book[asset]["asks"][lowest_ask]["id"][volume_traded:]

                    del self.__order_book[asset]["bids"][highest_bid]
                    del self.__priv_order_book[asset]["bids"][highest_bid]

                else:
                    del self.__order_book[asset]["bids"][highest_bid]
                    del self.__priv_order_book[asset]["bids"][highest_bid]
                    del self.__order_book[asset]["asks"][lowest_ask]
                    del self.__priv_order_book[asset]["asks"][lowest_ask]

                if asset in self.__position_cache:
                   self.__position_cache[asset] += np.concatenate((buyer_freqs, seller_freqs)).tolist()
                else:
                   self.__position_cache[asset] = np.concatenate((buyer_freqs, seller_freqs)).tolist()
                
                asset_bid_prices = np.array(list(self.__order_book[asset]["bids"].keys()))
                asset_ask_prices = np.array(list(self.__order_book[asset]["asks"].keys()))

                if asset_bid_prices.any(): highest_bid = np.max(asset_bid_prices)
                else: break
                if asset_ask_prices.any(): lowest_ask = np.min(asset_ask_prices)
                else: break


    def __update_order_book(self):
        for order in self.__order_cache:
            if order.get_asset() in order.get_owner().get_open_positions():
                positive_sum = order.get_owner().get_open_positions()[order.get_asset()]
                negative_sum = order.get_owner().get_open_positions()[order.get_asset()]
            else:
                positive_sum = 0
                negative_sum = 0

            for other_order in order.get_owner().get_open_orders().values():
                if other_order.get_size() < 0:
                    negative_sum += other_order.get_size()
                else:
                    positive_sum += other_order.get_size()

            if positive_sum <= order.get_owner().get_position_limits() and abs(negative_sum) <= order.get_owner().get_position_limits():
                self.__order_history.append(order)
                bid_or_ask = ["bids", "asks"][int(order.get_size() < 0)]
                
                if order.get_asset() not in self.__mkt_assets:
                    self.__mkt_assets.append(order.get_asset())
                    self.__order_book[order.get_asset()] = {
                        "bids": {},
                        "asks": {}
                    }
                    self.__priv_order_book[order.get_asset()] = {
                        "bids": {},
                        "asks": {}
                    }

                if order.get_price() in self.__order_book[order.get_asset()][bid_or_ask]:
                    self.__order_book[order.get_asset()][bid_or_ask][order.get_price()] += order.get_size()
                    self.__priv_order_book[order.get_asset()][bid_or_ask][order.get_price()]["owner"] = np.concatenate((self.__priv_order_book[order.get_asset()][bid_or_ask][order.get_price()]["owner"], [self.__mkt_participants.index(order.get_owner())] * abs(order.get_size())))
                    self.__priv_order_book[order.get_asset()][bid_or_ask][order.get_price()]["tick"] = np.concatenate((self.__priv_order_book[order.get_asset()][bid_or_ask][order.get_price()]["tick"], [self.__ticks_from_start] * abs(order.get_size())))
                    self.__priv_order_book[order.get_asset()][bid_or_ask][order.get_price()]["id"] = np.concatenate((self.__priv_order_book[order.get_asset()][bid_or_ask][order.get_price()]["id"], [self.__order_history.index(order) + 1] * abs(order.get_size())))
                else:
                    self.__order_book[order.get_asset()][bid_or_ask][order.get_price()] = order.get_size()
                    self.__priv_order_book[order.get_asset()][bid_or_ask][order.get_price()] = {}

                    self.__priv_order_book[order.get_asset()][bid_or_ask][order.get_price()]["owner"] = np.array([self.__mkt_participants.index(order.get_owner())] * abs(order.get_size()))
                    self.__priv_order_book[order.get_asset()][bid_or_ask][order.get_price()]["tick"] = np.array([self.__ticks_from_start] * abs(order.get_size()))
                    self.__priv_order_book[order.get_asset()][bid_or_ask][order.get_price()]["id"] = np.array([self.__order_history.index(order) + 1] * abs(order.get_size()))

                order.get_owner().update_open_orders(self, self.__order_history.index(order) + 1, order)

        self.__order_cache = []

    def __update_positions(self):
        for asset in self.__position_cache:
            for owner, id, position_update, cash_update in self.__position_cache[asset]:
                self.__mkt_participants[int(owner)].update_open_positions(self, asset, position_update, cash_update)
                self.__mkt_participants[int(owner)].get_open_orders()[int(id)].update_size(self, -position_update, int(id))

        self.__position_cache = {}

    def __clean_up(self):
        for participant in self.__mkt_participants:
            for open_order in participant.get_open_orders().values():
                del open_order

            for asset, open_position in participant.get_open_positions().items():
                print(participant.get_name(), "currently owns", open_position, asset, "and has cash balance", participant.get_cash())
                print(participant.get_name(), "owes/recieves", open_position, asset, "at market price", self.__mkt_assets_ltp[asset])
                participant.update_open_positions(self, asset, -open_position, self.__mkt_assets_ltp[asset] * open_position)
                print("Now", participant.get_name(), "has", participant.get_cash(), "in cash\n")
            
            participant.clean(self)

        for asset in self.__mkt_assets:
            self.__order_book[asset]["bids"].clear()
            self.__order_book[asset]["asks"].clear()
            self.__priv_order_book[asset]["bids"].clear()
            self.__priv_order_book[asset]["asks"].clear()

    def main_loop(self, ticks_to_run = float("inf")):
        while ticks_to_run > 0:
            self.__compute_next_tick()    #inbound orders
            self.__update_order_book()    #populate orderbook

            self.__all_book_history.append(copy.deepcopy(self.__priv_order_book)) #keep current book state for recording

            self.__evaluate_tick()        #match all orders
            self.__update_positions()     #update portfolios

            self.__ticks_from_start += 1
            ticks_to_run -= 1
            if self.__tick_rate: time.sleep(1 / self.__tick_rate())

        self.__clean_up() #clear all open orders and positions

    def visualize(self):
        order_size_cmap = LinearSegmentedColormap.from_list("order_size_cmap", [(0, "#00ff08"), 
                                                                                (.5, "#1fcc00"),
                                                                                (.5, "#9c0000"), 
                                                                                (1, "#ff0000")])
        
        for asset in self.__mkt_assets:
            for timestamp in range(len(self.__all_book_history)):
                if asset in self.__all_book_history[timestamp]:
                    order_sizes = np.array([len(order["id"]) for order in self.__all_book_history[timestamp][asset]["bids"].values()] + [-len(order["id"]) for order in self.__all_book_history[timestamp][asset]["asks"].values()])
                    order_size_colors = (order_sizes / max((abs(order_sizes))) + 1) / 2
                    order_size_alphas = abs(order_sizes) / max((abs(order_sizes))) / 4 * 3 + .25

                    plt.scatter([timestamp] * (len(self.__all_book_history[timestamp][asset]["bids"]) + len(self.__all_book_history[timestamp][asset]["asks"])), 
                                list(self.__all_book_history[timestamp][asset]["bids"].keys()) + list(self.__all_book_history[timestamp][asset]["asks"].keys()), 
                                c = order_size_colors, cmap = order_size_cmap, 
                                alpha = order_size_alphas, 
                                marker = "s", 
                                norm = Normalize(0, 1, True))

            plt.title(asset)
            plt.xlabel("Ticks")
            plt.ylabel("Price")
            plt.show()

    def animate(self):
        order_size_cmap = LinearSegmentedColormap.from_list("order_size_cmap", [(0, "#00ff08"), 
                                                                                (.5, "#1fcc00"), 
                                                                                (.5, "#9c0000"), 
                                                                                (1, "#ff0000")])
        
        for asset in self.__mkt_assets:
            tick_data = []
            tick_data_size = []

            for timestamp in range(len(self.__all_book_history)):
                order_sizes = np.array([len(order["id"]) for order in self.__all_book_history[timestamp][asset]["bids"].values()] + [-len(order["id"]) for order in self.__all_book_history[timestamp][asset]["asks"].values()])
                order_size_colors = (order_sizes / max((abs(order_sizes))) + 1) / 2
                order_size_alphas = abs(order_sizes) / max((abs(order_sizes))) / 4 * 3 + .25
                
                tick_data.append([[timestamp] * (len(self.__all_book_history[timestamp][asset]["bids"]) + len(self.__all_book_history[timestamp][asset]["asks"])), 
                                list(self.__all_book_history[timestamp][asset]["bids"].keys()) + list(self.__all_book_history[timestamp][asset]["asks"].keys()), 
                                order_size_colors, 
                                order_size_alphas])
                tick_data_size.append(len(self.__all_book_history[timestamp][asset]["bids"]) + len(self.__all_book_history[timestamp][asset]["asks"]))

            tick_data = np.concatenate(tick_data, axis = 1)
            tick_data_size = np.cumsum(tick_data_size)

            fig = plt.figure()
            ax = plt.axes(xlim=(0, len(self.__all_book_history)), ylim=(np.min(tick_data[1]), np.max(tick_data[1])))
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
            
            ani = FuncAnimation(fig, update, frames = range(len(self.__all_book_history)), interval = 100, blit = True, repeat = False)

            plt.title(asset)
            plt.xlabel("Ticks")
            plt.ylabel("Price")
            plt.show()