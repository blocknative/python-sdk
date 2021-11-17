"""Helper methods used throughout the codebase.
"""
from enum import Enum
from blocknative.exceptions import *


class ErrorReason(Enum):
    """Enum respresenting the different possible error states"""

    MESSAGE_TOO_LARGE = 'message too large'
    RATE_LIMIT = 'ratelimit'
    API_VERSION = 'api version not supported'
    API_KEY_MISSING = 'missing dappId'
    API_KEY_INVALID = 'is not a valid API key'
    EVENT_RATE_LIMIT = 'event rate limit'
    SIMULATED_RATE_LIMIT = 'Simulated transactions limit'


def raise_error_on_status(message: dict) -> None:
    """Raises an exception based on the error returned in the API server response

    Args:
        message_status: The status field of the API WebSocket message.

    Raises:
        WebsocketRateLimitError: If number of ws messages exceeds limit within a duration.
        MessageSizeError: The Websocket payload is too large.
        InvalidAPIVersionError: If using incorrect API version.
        EventRateLimitError: If the API key has exceeded its daily event limit.
        SimulatedEventRateLimitError: If the API key has exceeded its daily simulated event limit.
        IPRateLimitError: If the IP has exceeded its daily event limit.
        MissingAPIKeyError: If the API key is missing.
        InvalidAPIKeyError: If the API key is invalid.
        SDKError: If there is a non-specific error that is indicated by the server.
    """

    if message['status'] == 'ok' or 'reason' not in message:
        return None  # This message does not contain an error

    reason = message['reason'].rstrip().lstrip()
    
    if reason == ErrorReason.RATE_LIMIT.value:
        raise WebsocketRateLimitError(reason)
    elif reason == ErrorReason.MESSAGE_TOO_LARGE.value:
        raise MessageSizeError(reason)
    elif ErrorReason.API_KEY_MISSING.value in reason:
        raise MissingAPIKeyError(reason)
    elif reason == ErrorReason.API_VERSION.value:
        raise InvalidAPIVersionError(reason)
    elif ErrorReason.API_KEY_INVALID.value in reason:
        raise InvalidAPIKeyError(reason)
    elif ErrorReason.EVENT_RATE_LIMIT.value in reason:
        raise EventRateLimitError(reason)
    elif ErrorReason.SIMULATED_RATE_LIMIT.value in reason:
        raise SimulatedEventRateLimitError(reason)
    else:
        raise SDKError(reason)


def network_id_to_name(network_id: int) -> str:
    """Takes a network id and returns the network name.
    Args:
        network_id: The id of the network
    Returns:
        The network name.
    """
    return {
        1: 'main',
        3: 'ropsten',
        4: 'rinkeby',
        5: 'goerli',
        42: 'kovan',
        100: 'xdai',
        56: 'bsc-main',
    }[network_id]


def status_to_event_code(status: str):
    """
    Takes in the server status code ``status`` and returns the event code equivalent.
    """
    return {
        'sent': 'txSent',
        'pending': 'txPool',
        'pending-simulation': 'txPoolSimulation',
        'stuck': 'txStuck',
        'confirmed': 'txConfirmed',
        'failed': 'txFailed',
        'speedup': 'txSpeedUp',
        'cancel': 'txCancel',
        'dropped': 'txDropped',
    }[status]


def is_server_echo(event_code: str):
    """Determines if the ``event_code`` is an echo response from the server.

    Args:
        event_code: The event code from the server message.

    Returns:
        True for if it is a server echo message, False otherwise.
    """
    return event_code in {
        'txRequest',
        'nsfFail',
        'txRepeat',
        'txAwaitingApproval',
        'txConfirmReminder',
        'txSendFail',
        'txError',
        'txUnderPriced',
        'txSent',
    }


class SubscriptionType(Enum):
    """Enum representing the Subscription type.

    Attributes:
        ADDRESS: A subscription that subscribes to an address.
        TRANSACTION: A subscription that subscribes to an transaction.
    """

    ADDRESS = 0
    TRANSACTION = 1


def subscription_type(message: dict):
    """Determines the subscription type of websocket response message: `transaction` or `address`.
    Args:
        message: The websocket message.

    Returns:
        True if it is a transaction subscription and False otherwise.
    """
    if (
        'essentialFields' in message
        and message['event']['essentialFields']['watchedAddress'] == 'hash'
        or message['event']['categoryCode'] == 'activeTransaction'
    ):
        return SubscriptionType.TRANSACTION
    elif message['event']['categoryCode'] == 'activeAddress':
        return SubscriptionType.ADDRESS


def to_camel_case(string: str):
    """Converts the provided string into camel case
    Args:
        string: The string to convert
    Returns:
        The string in camel case
    """
    return ''.join(
        word.title() if idx > 0 else word for idx, word in enumerate(string.split('_'))
    )
