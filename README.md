<a href="https://pypi.org/project/blocknative-sdk/">
    <img src="https://img.shields.io/pypi/v/blocknative-sdk" />
</a>

# Blocknative Python SDK

## Install

VirtualEnv QuickStart

```bash
$ virtualenv bn
$ . ./bn/bin/activate
(bn) $ pip3 install --upgrade pip
(bn) $ pip3 install blocknative-sdk
(bn) $ curl 'https://raw.githubusercontent.com/blocknative/python-sdk/main/examples/subscribe.py' > subscribe.py
(bn) $ python3 subscribe.py myapikey.key
```

Manual Install

```bash
python3 setup.py install
```

## API Key

To get started using the Blocknative Python SDK you must first obtain an API Key. You can do so by heading over to [Blocknative.com](https://explorer.blocknative.com/account)!

## Usage

### Basic usage

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

### Unsubscribing

```python
from blocknative.stream import Stream
import json

# Initialize the stream
stream = Stream('<API_KEY>')

# Define your transaction handler
async def txn_handler(txn, unsubscribe):
    if txn['status'] == "confirmed":
        # Output the transaction data to the console
        print(json.dumps(txn, indent=4))

        # Unsubscribe from this subscription
        unsubscribe()

# Define the address you want to watch
uniswap_v2_address = '0x7a250d5630b4cf539739df2c5dacb4c659f2488d'

# Register the subscription
stream.subscribe_address(uniswap_v2_address, txn_handler)

# Start the websocket connection and start receiving events!
stream.connect()
```

### Using Filters

```python
from blocknative.stream import Stream
import json

stream = Stream('<API_KEY>')

async def txn_handler(txn, unsubscribe):
    # This will only get called with transactions that have status of 'confirmed'
    # This is due to the global filter above
    print(json.dumps(txn, indent=4))

uniswap_v2_address = '0x7a250d5630b4cf539739df2c5dacb4c659f2488d'

filters = [{
    'status': 'confirmed'
}]

# Global filter will apply to all of these subscriptions
stream.subscribe_address(curve_fi_address, txn_handler, filter=filters)

# Start the websocket connection and start receiving events!
stream.connect()
```

### Using Global Filters

Similar as above but this time we use global filters which will apply to all subscriptions.

```python
from blocknative.stream import Stream
import json

global_filters = [{
    'status': 'confirmed'
}]

stream = Stream('<API_KEY>', global_filters=global_filters)

async def txn_handler(txn, unsubscribe):
    # This will only get called with transactions that have status of 'confirmed'
    # This is due to the global filter above
    print(json.dumps(txn, indent=4))

uniswap_v2_address = '0x7a250d5630b4cf539739df2c5dacb4c659f2488d'
curve_fi_address = '0xdf5e0e81dff6faf3a7e52ba697820c5e32d806a8'
sushi_swap_address = '0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f'

# Global filter will apply to all of these subscriptions
stream.subscribe_address(curve_fi_address, txn_handler)
stream.subscribe_address(uniswap_v2_address, txn_handler)
stream.subscribe_address(sushi_swap_address, txn_handler)

# Start the websocket connection and start receiving events!
stream.connect()
```

### Connecting to Binance Smart Chain

```python
from blocknative.stream import Stream
import json

BSC_NETWORK_ID = 56

# Initialize the stream - specify network_id `56` to connect to bsc main
stream = Stream('<API_KEY>', network_id=BSC_NETWORK_ID)

# Define your transaction handler which has the context of a specific subscription.
async def txn_handler(txn, unsubscribe):
    # Output the transaction data to the console
    print(json.dumps(txn, indent=4))

# Define the address you want to watch
pancakeswap_v2_address = '0x10ed43c718714eb63d5aa57b78b54704e256024e'

# Register the subscription
stream.subscribe_address(pancakeswap_v2_address, txn_handler)

# Start the websocket connection and start receiving events!
stream.connect()
```
