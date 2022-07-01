# Getting Started

## Install

1. Make sure you're using Python 3.7 or newer.

2. `python3 -m pip install --upgrade blocknative-sdk`

3. Can you ``import blocknative``? If so then you're good to go!

## Usage

### Basic usage example

```python
from blocknative.stream import Stream
import json

# Initialize the stream
stream = Stream('<API_KEY>')

# Define your transaction handler which has the context of a specific subscription.
async def txn_handler(txn, unsubscribe):
    # Output the transaction data to the console
    print(json.dumps(txn, indent=4))

# Define the address you want to watch
uniswap_v2_address = '0x7a250d5630b4cf539739df2c5dacb4c659f2488d'

# Register the subscription
stream.subscribe_address(uniswap_v2_address, txn_handler)

# Start the websocket connection and start receiving events!
stream.connect()
```
