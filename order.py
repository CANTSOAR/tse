class Order():

    def __init__(self, asset, price, size, owner):
        self.asset = asset
        self.price = price #+ price is a bid, - price is an ask
        self.size = size
        self.owner = owner

    def update_size(self, update, id):
        self.size += update
        if not self.size:
            del self.owner._open_orders[id]
            del self

    def cancel_order(self):
        del self