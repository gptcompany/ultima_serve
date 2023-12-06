from redis import Redis
from cryptofeed import FeedHandler
from cryptofeed.callback import TradeCallback, BookCallback
from cryptofeed.defines import BID, ASK,TRADES, L3_BOOK, L2_BOOK, TICKER, OPEN_INTEREST, FUNDING, LIQUIDATIONS, BALANCES, ORDER_INFO
from cryptofeed.exchanges import BITFINEX, Bitfinex
#from app.Custom_Coinbase import CustomCoinbase
from cryptofeed.backends.redis import BookRedis, BookStream, CandlesRedis, FundingRedis, OpenInterestRedis, TradeRedis, BookSnapshotRedisKey
from decimal import Decimal
import asyncio
import logging
from datetime import datetime
logging.basicConfig(filename='var/log/bitfinex.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
async def trade(t, receipt_timestamp):
    assert isinstance(t.timestamp, float)
    assert isinstance(t.side, str)
    assert isinstance(t.amount, Decimal)
    assert isinstance(t.price, Decimal)
    assert isinstance(t.exchange, str)
    date_time = datetime.utcfromtimestamp(receipt_timestamp)

    # Extract milliseconds
    milliseconds = int((receipt_timestamp - int(receipt_timestamp)) * 1000)

    # Format the datetime object as a string and manually add milliseconds
    formatted_date = date_time.strftime('%Y-%m-%d %H:%M:%S.') + f'{milliseconds:03d}'
    print(f"Trade received at {formatted_date}: {t}")
    #await asyncio.sleep(0.2)

async def book(book, receipt_timestamp):
    date_time = datetime.utcfromtimestamp(receipt_timestamp)

    # Extract milliseconds
    milliseconds = int((receipt_timestamp - int(receipt_timestamp)) * 1000)

    # Format the datetime object as a string and manually add milliseconds
    formatted_date = date_time.strftime('%Y-%m-%d %H:%M:%S.') + f'{milliseconds:03d}'
    print(f"Book received at {formatted_date} for {book.exchange} - {book.symbol}, with {len(book.book)} entries. Top of book prices: {book.book.asks.index(0)[0]} - {book.book.bids.index(0)[0]}")
    if book.delta:
        print(f"Delta from last book contains {len(book.delta[BID]) + len(book.delta[ASK])} entries.")
    if book.sequence_number:
        assert isinstance(book.sequence_number, int)
    await asyncio.sleep(0.5)
async def aio_task():
    while True:
        print("Other task running")
        await asyncio.sleep(1)       
def main():
    path_to_config = '/config_cf.yaml'
    fh = FeedHandler(config=path_to_config)  
    symbols = fh.config.config['bf_symbols']
    fh.run(start_loop=False)
    fh.add_feed(BITFINEX, 
                # subscription={}, 
                # callbacks={},
                max_depth=60,
                subscription={
                    L3_BOOK: symbols, 
                    
                },
                callbacks={
                    L3_BOOK: book,#[
                        #BookCallback(book),
                        #BookCallback(
                            #BookRedis(
                            #host=fh.config.config['redis_host'], 
                            #port=fh.config.config['redis_port'], 
                            #snapshots_only=False,
                            #score_key='timestamp',
                            #                )
                            #         ),
                    #],
                },
                #cross_check=True,
                #timeout=-1
                )
    fh.add_feed(Bitfinex( 
                # subscription={}, 
                # callbacks={},
                #max_depth=100,
                subscription={
                    
                    TRADES: symbols,
                },
                callbacks={
                    
                    TRADES: trade,#[
                        #TradeCallback(trade),
                        #TradeCallback(
                            #TradeRedis(
                            #host=fh.config.config['redis_host'], 
                            #port=fh.config.config['redis_port'],
                            #                    )
                            #       ),
                    #],
                },
                #cross_check=True,
                #timeout=-1
                )
                )


    # This is for Bitfinex exchange not auth
    # fh.add_feed(Exchange(
    #             subscription={
    #             L3_BOOK: symbols, 
    #             TRADES: symbols,
    #             },
    #             callbacks={
    #                 L3_BOOK: [
    #                    BookCallback(book),
    #                     ],
    #                 TRADES: [
    #                    TradeCallback(trade),
    #                 ],
    #             },
    #             cross_check=True,
    #             #timeout=-1
    #             )
    # )

    loop = asyncio.get_event_loop()
    loop.create_task(aio_task())
    loop.run_forever()


if __name__ == '__main__':
    main()