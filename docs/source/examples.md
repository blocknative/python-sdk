# Examples


## ABI
If you include your ABI you will be able to get a decoded output of contract transactions. 

Example:

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
stream.subscribe_address(uniswap_v2_address, txn_handler, abi=abi)

# Start the websocket connection and start receiving events!
stream.connect()
```

## Loading Configuration
For those who have a config.json file downloaded from [MempoolExplorer](explorer.blocknative.com), you can use the following code snippet to
load this configuration file into your application.

Note: In the future this may be included in the sdk.

```python
import json
from blocknative.stream import Stream

API_KEY = ""

def load_config(BNStream: Stream, api_key: str, config_filename: str) -> Stream:
    """Loads a configuration from configuration.json file into a Stream.
    The `connect()` method will need to be called on the returned stream 
    initiate the connection to the server.

    Args:
        Stream: The uninitialised Stream
        api_key: The api key
        config_filename: The name of the config file to load

    Returns:
        The stream instance.
    """
    with open(config_filename, "r") as configs:
        configs = json.load(configs)
        global_filters = []
        subscriptions = []
        for config in configs:
            if config["name"] == "global":
                global_filters = config["filters"]
            subscription = {
                "name": config["name"],
                "address": config["id"],
                "abi": config["abi"] if "abi" in config else [],
                "filters": config["filters"],
            }
            subscriptions.append(subscription)

        stream = BNStream(api_key, global_filters=global_filters) if len(global_filters) else BNStream(api_key)

        for subscription in subscriptions:

            async def txn_handler(txn, unsubscribe):
                # Print out the name associated with the subscription (not required)
                print(subscription["name"])
                print(json.dumps(txn, indent=4))

            stream.subscribe_address(
                subscription["address"],
                filters=subscription["filters"],
                abi=subscription["abi"],
                callback=txn_handler,
            )
    return stream

stream = load_config(Stream, API_KEY, config_filename)
stream.connect()

```