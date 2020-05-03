class SmaSignal():

    action = None

    def __init__(self, market):
        self.market = market
        
        
    def get_direction(self):
        if self.past_close >= self.past_sma:
            return "long"
        else:
            return "short"
            
    def get_action(self):
        direction = self.get_direction()

        if self.status == "init_wait" and self.strategy == direction:
            return action

        if self.status == "out":
            action = "in" if self.strategy == direction else "wait_entry"
        if self.status == "in":
            action = "wait_exit" if self.strategy == direction else "out"

        return action


if __name__ == "__main__":
    SmaSignal("ETH-USDT")
