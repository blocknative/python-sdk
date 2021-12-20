"""
A simple example of subscribing to stream events
"""
import json
import sys
import traceback
import logging
import os
from blocknative.stream import Stream as BNStream
from blocknative.exceptions import SDKError

MONITOR_ADDRESS = 'bc1quv6lvq6ucc5w6yvl76dw4rs5n3ynt9xl09ygy7'

BN_API_KEY = os.getenv('BN_API_KEY', None)
BLOCKCHAIN = 'bitcoin'

async def txn_handler(txn, unsubscribe):
    """
    transaction handler for event stream
    """
    print(json.dumps(txn, indent=4))
    unsubscribe()

if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.DEBUG)

        if BN_API_KEY is None:
            logging.error('BN_API_KEY is required')
            sys.exit(1)

        stream = BNStream(BN_API_KEY, blockchain=BLOCKCHAIN, )
        stream.subscribe_address(MONITOR_ADDRESS, txn_handler)

        stream.connect()
    except SDKError as e:
        logging.error('API Failed: %s', str(e))
        traceback.print_exc(e)
