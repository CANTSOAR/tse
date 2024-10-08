from orderbook import Orderbook
from basic_bot1 import bBot1

o1 = bBot1("bot_1_oranges", 45, 55, 100, "oranges")
o2 = bBot1("bot_2_oranges", 50, 55, 50, "oranges")
o3 = bBot1("bot_3_oranges", 43, 47, 100, "oranges")
o4 = bBot1("bot_4_oranges", 45, 53, 50, "oranges")

k1 = bBot1("bot_1_kiwi", 127, 135, 1000, "kiwis")
k2 = bBot1("bot_2_kiwi", 130, 132, 500, "kiwis")
k3 = bBot1("bot_3_kiwi", 123, 129, 1000, "kiwis")
k4 = bBot1("bot_4_kiwi", 125, 133, 500, "kiwis")

#figure out how to make certain fields private/uneditable

book = Orderbook([o1, o2, o3, o4, k1, k2, k3, k4])
book.main_loop(100)
print(o1._open_positions, o2._open_positions, o3._open_positions, o4._open_positions)

print(k1._open_positions, k2._open_positions, k3._open_positions, k4._open_positions)

book.visualize()
book.animate()