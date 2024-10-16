from orderbook import Orderbook
from basic_bot import bBot1
from sample_algo import Algo

o1 = bBot1("bot_1_oranges", 48, 0, 100, 0, "oranges")
o2 = bBot1("bot_2_oranges", 0, 52, 0, 100, "oranges")

k1 = bBot1("bot_1_kiwi", 154, 158, 1000, 1000, "green kiwis")
k2 = bBot1("bot_2_kiwi", 150, 156, 1000, 1000, "green kiwis")

example_algo = Algo("sample")

#figure out how to make certain fields private/uneditable

book = Orderbook([o1, o2, k1, k2, example_algo])
book.main_loop(100)