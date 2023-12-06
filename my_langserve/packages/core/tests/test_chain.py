
import sys    
import os
print("In module products sys.path[0], __package__ ==", sys.path[0], __package__)
# Add the directory containing chain.py to the path
#sys.path.append(os.path.abspath('../core'))
from core import feed
from cryptofeed import FeedHandler
from cryptofeed.exchanges import Binance, COINBASE, BITFINEX, Bitfinex, BINANCE
from cryptofeed.exchanges import Coinbase
from cryptofeed.connection import AsyncConnection, RestEndpoint, Routes, WebsocketEndpoint
from cryptofeed.defines import  L3_BOOK, TRADES, BID, ASK
from decimal import Decimal
import time
import hashlib
import json
import hmac 
import base64

import logging
from colorama import init, Fore, Style
logging.basicConfig(filename='cryptofeed.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)



def test_chain():
    # print(
    #       chain.invoke({"test": "1+1=?"})
    #       )

    
    
    path_to_config = '/config_cf.yaml'
    #check if file exist
    assert os.path.exists(path_to_config), f"The file {path_to_config} does not exist!!!"
    print(f"The file {path_to_config} exists.")
        
    fh = FeedHandler(config=path_to_config)
    
    class CustomCoinbase(Coinbase):
        def __init__(self, callbacks=None, **kwargs):
            super().__init__(callbacks=callbacks, **kwargs)
            # we only keep track of the L3 order book if we have at least one subscribed order-book callback.
            # use case: subscribing to the L3 book plus Trade type gives you order_type information (see _received below),
            # and we don't need to do the rest of the book-keeping unless we have an active callback
            self.keep_l3_book = False
            if callbacks and L3_BOOK in callbacks:
                self.keep_l3_book = True
            self.__reset()

        def __reset(self):
            self.order_map = {}
            self.order_type_map = {}
            self.seq_no = None
            # sequence number validation only works when the FULL data stream is enabled
            chan = self.std_channel_to_exchange(L3_BOOK)
            if chan in self.subscription:
                pairs = self.subscription[chan]
                self.seq_no = {pair: None for pair in pairs}
            self._l3_book = {}
            self._l2_book = {}
                
            
        async def subscribe(self, conn:AsyncConnection):
            self.__reset()
            
            method =  'GET'
            request_path = "/users/self/verify"
            key = self.config['coinbase']['key_id']  #TODO: Try self.config['coinbase']['key_id'] instead of fh.config.config
            key_passphrase = self.config['coinbase']['key_passphrase']
            key_secret = self.config['coinbase']['key_secret']
            # print("Key:", key)
            # print("Passphrase:", key_passphrase)
            # print("Secret Key:", key_secret)
            timestamp = str(int(time.time()))
            message = timestamp + method + request_path
            hmac_key = base64.b64decode(key_secret)
            signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
            signature_b64 = base64.b64encode(signature.digest())
            for chan in self.subscription:
                    await conn.write(json.dumps({"type": "subscribe",
                                                "product_ids": list(self.subscription[chan]),
                                                "channels": [chan],
                                                "signature": signature_b64.decode(),
                                                "key": key,
                                                "passphrase":key_passphrase,
                                                "timestamp":timestamp,
                                                }))
            chan = self.std_channel_to_exchange(L3_BOOK)
            if chan in self.subscription:
                await self._book_snapshot(self.subscription[chan])
        
    # async def trade(t, receipt_timestamp):
    #         assert isinstance(t.timestamp, float)
    #         assert isinstance(t.side, str)
    #         assert isinstance(t.amount, Decimal)
    #         assert isinstance(t.price, Decimal)
    #         assert isinstance(t.exchange, str)
    #         print(f"Trade received at {receipt_timestamp}: {t}")     
        
    # async def book(book, receipt_timestamp):
    #     print(f'Book received at {receipt_timestamp} for {book.exchange} - {book.symbol}, with {len(book.book)} entries. Top of book prices: {book.book.asks.index(0)[0]} - {book.book.bids.index(0)[0]}')
    #     if book.delta:
    #         print(f"Delta from last book contains {len(book.delta[BID]) + len(book.delta[ASK])} entries.")
    #     if book.sequence_number:
    #         assert isinstance(book.sequence_number, int)
            
    # symbols = ['BTC-USDT', 'ETH-USDT']
    # fh.add_feed(CustomCoinbase(
    #                 subscription={
    #                 L3_BOOK: symbols, 
    #                 TRADES: symbols,
    #                 },
    #                 callbacks={
    #                     L3_BOOK: book,
    #                     TRADES: trade,
    #                     },
    #                 #cross_check=True,
    #                 #timeout=-1
    #                 )
    #     )
    symbols = ['BTC-USDT', 'ETH-USDT', 'ETH-BTC', 'BTC-USD']
    feed(fh, Bitfinex, symbols)
    feed(fh, CustomCoinbase, ['BTC-USDT', 'ETH-USDT', 'ETH-BTC', 'BTC-USD'])
    
    feed(fh, Binance, ['BTC-USDT', 'ETH-USDT', 'ETH-BTC'])
    fh.run()
    

    
if __name__ == "__main__":
    test_chain()
