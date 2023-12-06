from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from redis import Redis
from cryptofeed import FeedHandler
from cryptofeed.callback import TradeCallback, BookCallback
from cryptofeed.defines import BID, ASK,TRADES, L3_BOOK, L2_BOOK, TICKER, OPEN_INTEREST, FUNDING, LIQUIDATIONS, BALANCES, ORDER_INFO
from cryptofeed.exchanges import Binance, BITFINEX
from .Custom_Coinbase import CustomCoinbase
from cryptofeed.backends.redis import BookRedis, BookStream, CandlesRedis, FundingRedis, OpenInterestRedis, TradeRedis, BookSnapshotRedisKey
from decimal import Decimal
import asyncio
import logging
#from colorama import init, Fore, Style
logging.basicConfig(filename='feed.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)



def feed(fh, Exchange, symbols):
    """
    Connects a list of symbols to a given exchange.

    :param exchange: Exchange class from cryptofeed.exchanges (e.g., Binance)
    :param symbols: List of symbol strings (e.g., ['BTC-USD', 'ETH-USD'])
    """
    async def balance(b, receipt_timestamp):
        print(f"Balance update received at {receipt_timestamp}: {b}")


    async def position(p, receipt_timestamp):
        print(f"Position update received at {receipt_timestamp}: {p}")


    async def order_info(oi, receipt_timestamp):
        print(f"Order update received at {receipt_timestamp}: {oi}")
    async def ticker_update(ticker, receipt_timestamp):
        try:
        # Logic for handling ticker updates
            print(f"Ticker Update: {ticker}, Timestamp: {receipt_timestamp}")
        except Exception as e:
            logger.error(f"Error in ticker_update: {e}")
    async def trade(t, receipt_timestamp):
        assert isinstance(t.timestamp, float)
        assert isinstance(t.side, str)
        assert isinstance(t.amount, Decimal)
        assert isinstance(t.price, Decimal)
        assert isinstance(t.exchange, str)
        print(f"Trade received at {receipt_timestamp}: {t}")
        await asyncio.sleep(0.1)


    # Define a callback function for the L3 order book data
    async def book(book, receipt_timestamp):
        print(f'Book received at {receipt_timestamp} for {book.exchange} - {book.symbol}, with {len(book.book)} entries. Top of book prices: {book.book.asks.index(0)[0]} - {book.book.bids.index(0)[0]}')
        if book.delta:
            print(f"Delta from last book contains {len(book.delta[BID]) + len(book.delta[ASK])} entries.")
        if book.sequence_number:
            assert isinstance(book.sequence_number, int)
        await asyncio.sleep(0.1)

    # Adding the feed to the FeedHandler with respective callbacks
    print('hello')
    path_to_config = '/config_cf.yaml'
    if Exchange == BITFINEX:   
        fh.add_feed(Exchange, 
                    # subscription={}, 
                    # callbacks={},
                    subscription={
                        L3_BOOK: symbols, 
                        TRADES: symbols,
                    },
                    callbacks={
                        L3_BOOK: [
                            #BookCallback(book),
                            #BookCallback(
                                BookRedis(
                                #host=fh.config.config['redis_host'], 
                                #port=fh.config.config['redis_port'], 
                                snapshots_only=False,
                                #score_key='timestamp',
                                                )
                               #         ),
                        ],
                        TRADES: [
                            #TradeCallback(trade),
                            #TradeCallback(
                                TradeRedis(
                                #host=fh.config.config['redis_host'], 
                                #port=fh.config.config['redis_port'],
                                                    )
                                #       ),
                        ],
                    },
                    #cross_check=True,
                    #timeout=-1
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
    elif Exchange == Binance:
                
        fh.add_feed(Exchange(
                    config=path_to_config,
                    subscription={
                    L2_BOOK: symbols, 
                    TRADES: symbols,
                    },
                    callbacks={
                        L2_BOOK: [
                            BookCallback(book),
                                
                                ],
                        TRADES: [
                            TradeCallback(trade),
                                
                                ],
                        },
                    #cross_check=True
                    )
                    )
    
    else:
        fh.add_feed(Exchange(
                    config=path_to_config,
                    subscription={
                    L3_BOOK: symbols, 
                    TRADES: symbols,
                    },
                    callbacks={
                        L3_BOOK: [#book
                            #BookCallback(book),
                           #BookCallback(
                                BookRedis(
                                #host=fh.config.config['redis_host'], 
                                #port=fh.config.config['redis_port'], 
                                snapshots_only=False,
                                #score_key='timestamp'
                                                    )
                             #           ),
                        ],
                        TRADES: [
                            #TradeCallback(trade),
                           #TradeCallback(
                                TradeRedis(
                                #host=fh.config.config['redis_host'], 
                                #port=fh.config.config['redis_port'],
                                                    )
                             #           ),
                        ],
                        },
                    #cross_check=True,
                    #timeout=-1
                    )
        )
    
    return fh







# _prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are a helpful assistant who speaks like a pirate",
#         ),
#         ("human", "{text}"),
#     ]
# )
# _model = ChatOpenAI()

# # if you update this, you MUST also update ../pyproject.toml
# # with the new `tool.langserve.export_attr`
# chain = _prompt | _model
