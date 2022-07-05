"""
Blocknative Stream.
"""
import json
from datetime import datetime
import time
from dataclasses import dataclass, field
from queue import Queue, Empty
from typing import List, Mapping, Callable, Union
import trio
import logging
from logging import INFO
from trio_websocket import (
    open_websocket_url,
    ConnectionClosed,
    HandshakeError,
    WebSocketConnection,
)
from blocknative.utils import (
    raise_error_on_status,
    network_id_to_name,
    status_to_event_code,
    is_server_echo,
    subscription_type,
    SubscriptionType,
    to_camel_case,
)

from blocknative import __version__ as API_VERSION

FORMAT = "%(asctime)s [%(levelname)s]: %(message)s"
logging.basicConfig(format=FORMAT, level=INFO)

PING_INTERVAL = 15
PING_TIMEOUT = 10
MESSAGE_SEND_INTERVAL = 0.021  # 21ms

BN_BASE_URL = "wss://api.blocknative.com/v0"
BN_ETHEREUM = "ethereum"
BN_ETHEREUM_ID = 1
BN_STREAM_CLASS_VERSION = "1.1"

Callback = Callable[[dict, Callable], None]


@dataclass
class Subscription:
    """Dataclass representing the Subscription object.

    Attributes:
        callback: Callback function that will get executed for this subscription.
        data: Data associated with a subscription.
        sub_type: The type of subscription - `ADDRESS` or `TRANSACTION`.
    """

    callback: Callback
    data: dict
    sub_type: SubscriptionType


@dataclass
class Config:
    """Dataclass representing the client configuration object.

    Attributes:
        scope: The Ethereum or Bitcoin address that this configuration applies to,
        or `global` to apply the configuration gobally.
        filters: The array of valid filters. The Blocknative service uses jsql, a JavaScript query
        language to filter events.
        abi: The valid JSON ABI that will be used to decode input data for transactions
        that occur on the contract address defined in `scope`.
        watch_address: Defines whether the service should automatically watch the
        address as defined in `scope`.
    """

    scope: str
    filters: List[dict] = None
    abi: List[dict] = None
    watch_address: bool = True

    def as_dict(self) -> dict:
        """Filters out the None values.
        Returns:
            The Config class as a dict excluding fields with a None value.
        """
        return {
            "config": {
                to_camel_case(key): self.__dict__[key]
                for key in self.__dict__
                if self.__dict__[key] is not None
            }
        }


class Stream:
    """Stream class used to connect to Blocknative's WebSocket API.

    Args:

        api_key: The api key. Get one at `blocknative.com <https://explorer.blocknative.com/?signup=true/>`_.
        blockchain: The blockchain you want to connect to. Default is ``ethereum``.
        network_id: The id of the network. For instance, ``4`` for Ethereum Rinkeby.
        global_filters: The filters that will be applied globally to the stream.
    """

    api_key: str
    blockchain: str = BN_ETHEREUM
    network_id: int = BN_ETHEREUM_ID
    version: str = BN_STREAM_CLASS_VERSION
    global_filters: List[dict] = None
    valid_session: bool = True
    _ws: WebSocketConnection = None
    _message_queue: Queue = Queue()
    _subscription_registry: Mapping[str, Subscription] = {}

    def __init__(
        self,
        api_key: str,
        blockchain: str = BN_ETHEREUM,
        network_id: int = BN_ETHEREUM_ID,
        global_filters: List[dict] = global_filters,
    ):
        self.api_key = api_key
        self.blockchain = blockchain
        self.network_id = network_id
        self.global_filters = global_filters

    def subscribe_address(
        self,
        address: str,
        callback: Callback,
        filters: List[dict] = None,
        abi: Union[List[dict], str] = None,
    ):
        """Subscribes to an address to listen to any incoming and
        outgoing transactions that occur on that address.

        Args:
            address: The address to watch for incoming and outgoing transactions.
            callback: The callback function that will get executed for this subscription.
            filters: The filters by which to filter the transactions associated with the address.
            abi: The ABI of the contract. Used if `address` is a contract address.
        """

        if self.blockchain == BN_ETHEREUM:
            address = address.lower()

        if isinstance(abi, str):
            abi = json.loads(abi)

        # Add this subscription to the registry
        self._subscription_registry[address] = Subscription(
            callback,
            {"filters": filters, "abi": abi},
            SubscriptionType.ADDRESS,
        )

        # Only send the message if we are already connected. The connection handler
        # will send the messages within the registry upon connect.
        if self._is_connected():
            self._send_config_message(address, True, filters)

    def subscribe_txn(self, tx_hash: str, callback: Callback, status: str = "sent"):
        """Subscribes to an transaction to listen to transaction state changes.

        Args:
            txn_hash: The hash of the transaction to watch.
            callback: The callback function that will get executed for this subscription.
            status: The status of the transaction to receive events for. Leave out for all events.
        """
        # Add this subscription to the registry
        self._subscription_registry[tx_hash] = Subscription(
            callback, status, SubscriptionType.TRANSACTION
        )

        # Only send the message if we are already connected. The connection handler
        # will send the messages within the registry upon connect.
        if self._is_connected():
            self._send_txn_watch_message(tx_hash, status)

    def connect(self, base_url: str = BN_BASE_URL):
        """Initializes the connection to the WebSocket server.

        Args:
            base_url: The websocket url to connect to. Useful for when using a proxy.
        """
        try:
            return trio.run(self._connect, base_url)
        except KeyboardInterrupt:
            print("keyboard interrupt")
            return None

    def send_message(self, message: str):
        """Sends a websocket message. (Adds the message to the queue to be sent).

        Args:
            message: The message to send.
        """
        self._message_queue.put(message)
        logging.debug("Sending: %s", message)

    async def _message_dispatcher(self):
        """In a loop: Polls send message queue for latest messages to send to server.

        Waits ``MESSAGE_SEND_INTERVAL`` seconds before sending the next message
        in order to comply with the server's limit of 50 messages per second

        Note:
            This function runs until cancelled.
        """
        while self.valid_session:
            try:
                msg = self._message_queue.get_nowait()
                await self._ws.send_message(json.dumps(msg))
            except Empty:
                pass
            finally:
                await trio.sleep(MESSAGE_SEND_INTERVAL)

    async def _poll_messages(self):
        """In a loop: Polls ``ws`` message queue for latest WebSocket message.

        Note:
            This function runs until cancelled.
        """
        while self.valid_session:
            msg = await self._ws.get_message()
            await self._message_handler(json.loads(msg))

    async def _message_handler(self, message: dict):
        """Handles incoming WebSocket messages.

        Note:
            This function runs until cancelled.

        Args:
            message: The incoming websocket message.
        """
        # This should never happen but indicates an invalid message from the server
        if not "status" in message:
            self.valid_session = False
            return

        # Raises an exception if the status of the message is an error
        raise_error_on_status(message)

        if "event" in message:
            event = message["event"]
            # Ignore server echo and unsubscribe messages
            if is_server_echo(event["eventCode"]):
                return

            if "transaction" in event:
                event_transaction = event["transaction"]
                # Checks if the messsage is for a transaction subscription
                if subscription_type(message) == SubscriptionType.TRANSACTION:
                    # Find the matching subscription and run it's callback
                    transaction_hash = event_transaction["hash"]
                    if transaction_hash in self._subscription_registry:
                        transaction = self._flatten_event_to_transaction(event)
                        await self._subscription_registry[transaction_hash].callback(
                            transaction
                        )

                # Checks if the messsage is for an address subscription
                elif subscription_type(message) == SubscriptionType.ADDRESS:
                    watched_address = event_transaction["watchedAddress"]
                    if (
                        watched_address in self._subscription_registry
                        and watched_address is not None
                    ):
                        # Find the matching subscription and run it's callback
                        transaction = self._flatten_event_to_transaction(event)
                        await self._subscription_registry[watched_address].callback(
                            transaction, (lambda: self.unsubscribe(watched_address))
                        )

    def unsubscribe(self, watched_address):
        """Unsubscribe from the current stream.

        Note:
            This function is passed as a parameter to the to the transaction callback that you provide.

        Args:
            watched_address: The address to unsubscribe from.
        """

        # remove this subscription from the registry so that we don't execute the callback
        del self._subscription_registry[watched_address]

        def _unsubscribe(_):
            self.send_message(
                self._build_payload(
                    category_code="accountAddress",
                    event_code="unwatch",
                    data={"account": {"address": watched_address}},
                )
            )

        return _unsubscribe

    async def _heartbeat(self):
        """Send periodic pings on WebSocket.

        Wait up to ``PING_TIMEOUT`` seconds to send a ping and receive a pong. Raises
        ``TooSlowError`` if the timeout is exceeded. If a pong is received, then
        wait ``PING_INTERVAL`` seconds before sending the next ping.

        Note:
            This function runs until cancelled.

        Raises:
            ConnectionClosed: if websocket is closed.
            TooSlowError: if the timeout expires.
        """

        while True:
            with trio.fail_after(PING_TIMEOUT):
                await self._ws.ping()
            await trio.sleep(PING_INTERVAL)

    async def _handle_connection(self, base_url: str):
        """Handles the setup once the websocket connection is established, as well as,
        handles reconnect if the websocket closes for any reason.

        Note:
            This function runs until cancelled.
        """

        # If the user set global_filters then send them once _message_dispatcher starts
        if self.global_filters:
            self._send_config_message("global", None, self.global_filters)

        # Queues up the init message which will be sent once _message_dispatcher starts
        self._queue_init_message()

        # Iterate over the registered subscriptions and push them onto the message queue
        for sub_id, subscription in self._subscription_registry.items():
            if subscription.sub_type == SubscriptionType.TRANSACTION:
                self._send_txn_watch_message(sub_id, status=subscription.data)
            elif subscription.sub_type == SubscriptionType.ADDRESS:
                self._send_config_message(
                    sub_id, True, subscription.data["filters"], subscription.data["abi"]
                )

        try:
            async with trio.open_nursery() as nursery:
                nursery.start_soon(self._heartbeat)
                nursery.start_soon(self._poll_messages)
                nursery.start_soon(self._message_dispatcher)
        except (ConnectionClosed, trio.MultiError, trio.TooSlowError) as error:
            if isinstance(error, trio.TooSlowError):
                logging.warn(
                    f"Server failed to respond to ping within the given timeout of {PING_TIMEOUT} seconds."
                )
            logging.info("Attempting to reconnect...")
            # If server times the connection out or drops, reconnect
            await trio.sleep(0.5)
            await self._connect(base_url)

    async def _connect(self, base_url):
        try:
            async with open_websocket_url(base_url) as ws:
                self._ws = ws
                await self._handle_connection(base_url)
        except HandshakeError as e:
            logging.exception("Handshake failed")
            return False

    def _is_connected(self) -> bool:
        """Tests whether the websocket is connected.

        Returns:
            True if the websocket is connected, False otherwise.
        """
        return self._ws and not self._ws.closed

    def _send_config_message(
        self,
        scope,
        watch_address=True,
        filters: List[dict] = None,
        abi: List[dict] = None,
    ):
        """Helper method which constructs and sends the payload for watching addresses.

        Args:
            scope: The scope which this config applies to.
            watch_address: Indicates whether or not to watch the address  (if scope ==  `address`).
            filters: Filters used to filter out transactions for the given scope.
            abi: The ABI of the contract. Used if `scope` is a contract address.
        """
        self.send_message(
            self._build_payload(
                category_code="configs",
                event_code="put",
                data=Config(scope, filters, abi, watch_address).as_dict(),
            )
        )

    def _send_txn_watch_message(self, txn_hash: str, status: str = "sent"):
        """Helper method which constructs and sends the payload for watching transactions.

        Args:
            txn_hash: The hash of the transaction to watch.
            status: The status of the transaction to receive events for.
        """
        txn = {
            "transaction": {
                "hash": txn_hash,
                "startTime": int(time.time() * 1000),
                "status": status,
            }
        }
        self.send_message(
            self._build_payload(
                "activeTransaction",
                event_code=status_to_event_code(status),
                data=txn,
            )
        )

    def _build_payload(
        self,
        category_code: str,
        event_code: str,
        data: Union[Config, Mapping[str, str]] = {},
    ) -> dict:
        """Helper method to construct the payload to send to the server.

        Args:
            category_code: The category code associated with the event.
            event_code: The event code associated with the event.
            data: The data associated with this payload. Can be a configuration object
            for filtering and watching addresses or an object for watching transactions.

        Returns:
            The constructed payload to send to the server.
        """
        return {
            "timeStamp": datetime.now().isoformat(),
            "dappId": self.api_key,
            "version": API_VERSION,
            "blockchain": {
                "system": self.blockchain,
                "network": network_id_to_name(self.network_id),
            },
            "categoryCode": category_code,
            "eventCode": event_code,
            **data,
        }

    def _queue_init_message(self):
        """Sends the initialization message e.g. the checkDappId event."""
        self.send_message(
            self._build_payload(category_code="initialize", event_code="checkDappId")
        )

    def _flatten_event_to_transaction(self, event: dict):
        transaction = {}
        eventcopy = dict(event)
        del eventcopy["dappId"]
        if "transaction" in eventcopy:
            txn = eventcopy["transaction"]
            for k in txn.keys():
                transaction[k] = txn[k]
            del eventcopy["transaction"]
        if "blockchain" in eventcopy:
            bc = eventcopy["blockchain"]
            for k in bc.keys():
                transaction[k] = bc[k]
            del eventcopy["blockchain"]
        if "contractCall" in eventcopy:
            transaction["contractCall"] = eventcopy["contractCall"]
            del eventcopy["contractCall"]
        for k in eventcopy:
            if not isinstance(k, dict) and not isinstance(k, list):
                transaction[k] = eventcopy[k]
        return transaction
