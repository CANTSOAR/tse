from orderbook import Orderbook
from basic_bot import bBot1
from sample_algo import Algo

o1 = bBot1("bot_1_oranges", 48, 0, 100, 0, "oranges")
o2 = bBot1("bot_2_oranges", 0, 52, 0, 100, "oranges")

k1 = bBot1("bot_1_kiwi", 154, 158, 1000, 1000, "green kiwis")
k2 = bBot1("bot_2_kiwi", 150, 156, 1000, 1000, "green kiwis")

example_algo = Algo()

#figure out how to make certain fields private/uneditable

participants = [o1, o2, k1, k2, example_algo]
trials = []

for x in range(100):
    print(x, [participant.get_cash() for participant in participants])
    total_sum1 = 0
    for participant in participants:
        total_sum1 += participant.get_cash()

    book = Orderbook(participants)
    book.main_loop(100)
    book.main_loop(100)

    total_sum2 = 0
    for participant in participants:
        total_sum2 += participant.get_cash()

    trials.append([total_sum1, total_sum2])


print(trials)