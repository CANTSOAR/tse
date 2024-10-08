from participant import Participant
from order import Order

class Algo(Participant):

    #DO NOT TOUCH
    def __init__(self, name):
        super().__init__(name)

    def evaluate_tick(self, order_book_data):
        #
        #
        #    This function is called once every tick
        #    Put trading logic here
        #    Can use all of the data from orderbook
        #    Be careful what orders you are creating
        #    You must create orders using the Order class
        #    Return the orders in a list
        #
        #

        return [] #must return an array of orders