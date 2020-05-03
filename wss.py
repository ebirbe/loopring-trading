import json
import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time


def on_message(ws, message):

    # ~ print(message)

    if message == "ping":
        ws.send("pong")
        return

    data = json.loads(message)
    if not data.get("data"):
        return

    bid = float(data["data"][9])
    ask = float(data["data"][10])
    spread = ask - bid
    middle = (bid + ask) / 2
    percent =  ((middle - bid ) * 100) / middle
    print("Spread: %.2f Percent: %.2f%% Middle: %.2f" % (spread, percent, middle) )


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
                }
            ]
        })
        ws.send(suscription)

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    ws = websocket.WebSocketApp("wss://ws.loopring.io/v2/ws",
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
