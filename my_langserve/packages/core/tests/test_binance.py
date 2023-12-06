from cryptofeed import FeedHandler
from cryptofeed.defines import BALANCES, ORDER_INFO, POSITIONS, L3_BOOK, L2_BOOK, TRADES, BID, ASK
from cryptofeed.exchanges import Binance, BinanceDelivery, BinanceFutures
from cryptofeed.callback import TradeCallback, BookCallback
import asyncio
from decimal import Decimal


async def balance(b, receipt_timestamp):
    print(f"Balance update received at {receipt_timestamp}: {b}")


async def position(p, receipt_timestamp):
    print(f"Position update received at {receipt_timestamp}: {p}")


async def order_info(oi, receipt_timestamp):
    print(f"Order update received at {receipt_timestamp}: {oi}")

async def trade(t, receipt_timestamp):
        assert isinstance(t.timestamp, float)
        assert isinstance(t.side, str)
        assert isinstance(t.amount, Decimal)
        assert isinstance(t.price, Decimal)
        assert isinstance(t.exchange, str)
        print(f"Trade received at {receipt_timestamp}: {t}")
        #await asyncio.sleep(1)


    # Define a callback function for the L3 order book data
async def book(book, receipt_timestamp):
    print(f'Book received at {receipt_timestamp} for {book.exchange} - {book.symbol}, with {len(book.book)} entries. Top of book prices: {book.book.asks.index(0)[0]} - {book.book.bids.index(0)[0]}')
    if book.delta:
        print(f"Delta from last book contains {len(book.delta[BID]) + len(book.delta[ASK])} entries.")
    if book.sequence_number:
        assert isinstance(book.sequence_number, int)
    #await asyncio.sleep(1)
def main():
    path_to_config = '/config_cf.yaml'

    #binance = Binance(subscription={BALANCES: ['BTC-USDT'], ORDER_INFO: []}, timeout=-1, callbacks={BALANCES: balance, ORDER_INFO: order_info})
    #binance_delivery = BinanceDelivery(config=path_to_config, subscription={BALANCES: [], POSITIONS: [], ORDER_INFO: []}, timeout=-1, callbacks={BALANCES: balance, POSITIONS: position, ORDER_INFO: order_info})


    

    symbols = ['BTC-USDT', 'ETH-USDT', 'ETH-BTC', 'BTC-USD']
    f = FeedHandler(config=path_to_config)
    binance1 = Binance(config=path_to_config, subscription={BALANCES: [], ORDER_INFO: []}, timeout=-1, callbacks={BALANCES: balance, ORDER_INFO: order_info})
    f.add_feed(binance1)
    api = f.feeds[0]
    #f.add_feed(binance_delivery)
    print(api._generate_token())
    #print(binance_delivery._generate_token())
    print(api.balances_sync())
    print(api.orders_sync())
    binance2 = Binance(config=path_to_config,
                    subscription={
                    L2_BOOK: symbols, 
                    TRADES: symbols,
                    },
                    callbacks={
                        L2_BOOK: book,
                        TRADES: [TradeCallback(trade),
                                
                                ],
                        },
                    cross_check=True
                    )
    f.add_feed(binance2)
    api2 = f.feeds[1]
    #f.add_feed(binance_delivery)
    print(api2._generate_token())
    #print(binance_delivery._generate_token())
    print(api2.balances_sync())
    print(api2.orders_sync())
    f.run()


if __name__ == '__main__':
    main()