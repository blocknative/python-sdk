from blocknative.stream import Stream as BNStream
import json,sys,traceback
import logging

monitor_address = '0x7a250d5630b4cf539739df2c5dacb4c659f2488d'

class Printer:
    REQUIRED_TXN = 10
    
    def __init__(self):
        self.transaction_count = self.REQUIRED_TXN
        
    async def on_transaction(self, txn, unsubscribe):
        print(json.dumps(txn, indent=4))
        if txn['status'] == 'confirmed':
            self.transaction_count -= 1
            if self.transaction_count < 1:
                unsubscribe()

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
                printer = Printer()
                server_filter = [{'status':'confirmed'}]
                stream.subscribe_address(monitor_address, (lambda txn, callback: printer.on_transaction(txn, callback)), filters=server_filter)
                stream.connect()
    except Exception as e:
        print('API Failed: %s' % str(e))
        traceback.print_exc(e)
