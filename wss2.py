import json
import websocket

try:
    import thread
except ImportError:
    import _thread as thread
import time


class OrderBook():

    bids = None
    asks = None
    spread = None
    spread_percent = None
    middle_price = None

    def __init__(self, market):
        self.name = name

    def _update(self):
        bid = float(self.bids[0][0])
        ask = float(self.asks[0][0])
        self.spread = ask - bid
        self.middle_price = (bid + ask) / 2
        self.slippage =  ((middle - bid ) * 100) / middle
        

    def read_data(self, data):
        self.bids = data["bids"]
        self.asks = data["asks"]
        self._update()


class LoopringWebSocket():

    ws = None
    market = None

    def __init__(self, market):
        self.market = market

    def on_message(self, ws, message):

        print(message)

        if message == "ping":
            ws.send("pong")
            return

        data = json.loads(message)
        if not data.get("data"):
            return

        

        # ~ bid = float(data["data"][9])
        # ~ ask = float(data["data"][10])
        # ~ spread = ask - bid
        # ~ middle = (bid + ask) / 2
        # ~ percent =  ((middle - bid ) * 100) / middle
        # ~ print("Spread: %.2f Percent: %.2f%% Middle: %.2f" % (spread, percent, middle))


    def on_error(self, error):
        print(error)


    def on_close(self):
        print("### closed ###")


    def on_open(self):

        def run(*args):
            suscription = json.dumps({
                "op": "sub",
                "unsubscribeAll": True,
                "topics": [
                    {
                        "topic": "ticker",
                        "market": "ETH-USDT",
                    },
                    {
                      "topic": "orderbook",
                      "market": "ETH-USDT",
                      "level": 0,
                      "count": 1,
                      "snapshot": True,
                    },
                ]
            })
            ws.send(suscription)

        thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "wss://ws.loopring.io/v2/ws",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close)
    ws.run_forever()
