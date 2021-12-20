"""subscribe bsc example"""
import json
import sys
import traceback
import logging
from blocknative.stream import Stream as BNStream
from blocknative.exceptions import SDKError

NETWORK_ID = 56
PANCAKESWAP_V2_ADDRESS = '0x10ed43c718714eb63d5aa57b78b54704e256024e'

async def txn_handler(txn, unsubscribe):
    """Output the transaction data to the console"""
    _  = unsubscribe
    print(json.dumps(txn, indent=4))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('%s apikey' % sys.argv[0])
    else:
        try:
            logging.basicConfig(level=logging.INFO)
            apikeyfile = sys.argv[1]
            with open(apikeyfile, 'r') as apikey:
                keystring = apikey.readline().rstrip().lstrip()
                stream = BNStream(keystring, network_id=NETWORK_ID)
                stream.subscribe_address(PANCAKESWAP_V2_ADDRESS, txn_handler)
                stream.connect()
        except SDKError as e:
            logging.error('API Failed: %s', str(e))
            traceback.print_exc(e)
