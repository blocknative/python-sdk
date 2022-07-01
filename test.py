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


stream = load_config(Stream, API_KEY, "bsc-config.json")
stream.connect()

from blocknative.stream import Stream
import json
from blocknative.stream import Stream as BNStream

API_KEY = '8e104d22-fe9d-4f49-b772-8583086c709e' #'941fcff3-d6f7-4450-aa04-3be24c063996'

# Initialize the stream - specify network_id 56 to connect to bsc main

# Define your transaction handler which has the context of a specific subscription.
async def txn_handler(txn, unsubscribe):
    # Output the transaction data to the console
    print(json.dumps(txn, indent=4))

def main():
    stream = Stream(API_KEY, network_id=250)

    # Register the subscription
    stream.subscribe_address(API_KEY, txn_handler)

    # Start the websocket connection and start receiving events!
    stream.connect('wss://staging.api.blocknative.com')

main()
