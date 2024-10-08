class Participant():

    def __init__(self, name, cash = 1000):
        self._name = name
        self._cash = cash
        self._open_orders = {}
        self._open_positions = {}
    
    def _update_positions(self, asset, position_update, cash_change):
        self._cash += cash_change

        if asset in self._open_positions:
            self._open_positions[asset] += position_update
        else:
            self._open_positions[asset] = position_update

    def cash(self):
        return self._cash
