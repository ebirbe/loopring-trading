import json
import websocket

try:
    import thread
except ImportError:
    import _thread as thread
import time


bid = None
ask = None

def refresh_spread(new_bid, new_ask):

    global bid
    global ask

    bid = new_bid
    ask = new_ask

    spread = ask - bid
    middle = (bid + ask) / 2
    percent =  ((middle - bid ) * 100) / middle
    print("Spread: %.8f Percent: %.2f%% Middle: %.8f" % (spread, percent, middle) )
    

def read_orderbook(content):
    data = content['data']
    new_bid = float(data.get('bids')[0][0])
    new_ask = float(data.get('asks')[0][0])


    if all([bid == new_bid, ask == new_ask]):
        return

    refresh_spread(new_bid, new_ask)

def on_message(ws, message):

    #print(message)

    if message == "ping":
        ws.send("pong")
        return

    data = json.loads(message)
    if not data.get("data"):
        return

    if data.get("topic")["topic"] == "orderbook":
        read_orderbook(data)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):

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
                  #"market": "ETH-USDT",
                  "market": "LRC-ETH",
                  "level": 0,
                  "count": 1,
                  "snapshot": True,
                },
            ]
        })
        ws.send(suscription)

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://ws.loopring.io/v2/ws",
                              on_message=on_message,
                              on_error=on_error,
                              on_open=on_open,
                              on_close=on_close)
    ws.run_forever()
