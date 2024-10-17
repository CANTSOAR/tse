from participant import Participant
from order import Order

class Algo(Participant):

    #ONLY CHANGE NAME
    def __init__(self):
        super().__init__("[[NAME HERE]]")

    def evaluate_tick(self, order_book_data):
        #
        #
        #    This function is called once every tick
        #    Put trading logic here
        #    Can use all of the data from orderbook
        #    Be careful what orders you are creating
        #    You must create orders using the Order class
        #    Return the orders in a list
        #    See example for some ideas (hopefully better than example)
        #
        #

        return [] #must return an array of orders