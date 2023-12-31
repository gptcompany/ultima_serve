from cryptofeed import FeedHandler
from cryptofeed.defines import BUY, LIMIT
from cryptofeed.exchanges import BITFINEX
import os

def main():
    path_to_config = '/config_cf.yaml'
    assert os.path.exists(path_to_config), f"The file {path_to_config} does not exist!!!"
    print(f"The file {path_to_config} exists.")
    
    f = FeedHandler(config=path_to_config)
    f.add_feed(BITFINEX, subscription={}, callbacks={})
    api = f.feeds[0]
    print(api.balances_sync())
    print(api.orders_sync())
    #order = api.place_order_sync('BTC-USD', BUY, LIMIT, 0.0001, 2000)
    #print(order)
    print(api.orders_sync(symbol='BTC-USD'))
    #print(api.cancel_order_sync(order[4][0][0], symbol='BTC-USD'))
    print(api.orders_sync(symbol='BTC-USD'))

    f.run()


if __name__ == '__main__':
    main()