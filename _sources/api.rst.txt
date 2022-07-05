Application Programming Interface
=================================

.. autoclass:: blocknative.stream.Stream

        api_key: The api key. Get one at `blocknative.com <https://explorer.blocknative.com/?signup=true/>`_.
        blockchain: The blockchain you want to connect to. Default is ``ethereum``.
        network_id: The id of the network. For instance, ``4`` for Ethereum Rinkeby.
        global_filters: The filters that will be applied globally to the stream.


.. code-block:: python

    API_KEY = '' # Get one at https://explorer.blocknative.com/?signup=true
    blockchain = 'ethereum'
    network_id = 4
    # This will be applied to all streams.
    global_filters = [{ "status": "pending" }]
    Stream(API_KEY, BLOCKCHAIN, network_id, global_filters)

.. autofunction:: blocknative.stream.Stream.connect

.. autofunction:: blocknative.stream.Stream.subscribe_address


.. code-block:: python

    stream = Stream(API_KEY)

    # Define the address you want to watch
    address = '0x7a250d5630b4cf539739df2c5dacb4c659f2488d'

    # Define your transaction handler which has the context of a specific subscription.
    async def callback(txn, unsubscribe):
        # Output the transaction data to the console
        print(json.dumps(txn, indent=4))

    stream.subscribe_address(address, callback, filters=[{"status": "pending"}])


.. autofunction:: blocknative.stream.Stream.subscribe_txn