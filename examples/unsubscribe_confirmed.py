from blocknative.stream import Stream as BNStream
import json,sys,traceback

monitor_address = '0x7a250d5630b4cf539739df2c5dacb4c659f2488d'

async def txn_handler(txn, unsubscribe):
    print(json.dumps(txn, indent=4))
    if 'status' in txn and txn['status'] == 'confirmed':
      unsubscribe()

if __name__ == '__main__':
    try:
        if len(sys.argv) == 1:
            print('{} apikey' % sys.argv[0])
        else:
            apikeyfile = sys.argv[1]
            with open(apikeyfile, 'r') as apikey:
                keystring = apikey.readline().rstrip().lstrip()
                stream = BNStream(keystring)
                stream.subscribe_address(monitor_address, txn_handler)
                stream.connect()
    except Exception as e:
        print('API Failed: ' + str(e))
        traceback.print_exc(e)