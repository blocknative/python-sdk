from blocknative.stream import Stream as BNStream
import json,sys,traceback,logging

monitor_address = '0x7a250d5630b4cf539739df2c5dacb4c659f2488d'

async def txn_handler(txn, unsubscribe):
    print(json.dumps(txn, indent=4))

if __name__ == '__main__':
    try:
        if len(sys.argv) == 1:
            print('%s apikey' % sys.argv[0])
        else:
            logging.basicConfig(level=logging.INFO)            
            apikeyfile = sys.argv[1]
            with open(apikeyfile, 'r') as apikey:
                keystring = apikey.readline().rstrip().lstrip()
                stream = BNStream(keystring)
                stream.subscribe_address(monitor_address, txn_handler)
                stream.connect()
    except Exception as e:
        print('API Failed: %s' % str(e))
        traceback.print_exc(e)
