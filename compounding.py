class CompoundWallet:
    def __init__(self, capital):
        self.capital = capital

    def apply_return(self, percentage_gain):
        self.capital *= (1 + percentage_gain / 100)