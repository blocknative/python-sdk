from enum import Enum
from blocknative.exceptions import *
from dataclasses import dataclass


class ErrorReason(Enum):
    MESSAGE_TOO_LARGE = "message too large"
    RATE_LIMIT = "ratelimit"
    API_VERSION = "api version not supported"
    API_KEY_MISSING = "missing dappId"
    API_KEY_INVALID = "is not a valid API key"


def status_error_to_exception(message: dict) -> None:
    """Raises an exception based on the error returned in the API server response

    Args:
        message_status: The status field of the API WebSocket message.

    Raises:
        WebsocketRateLimitError: iIf number of ws messages exceeds limit within a duration.
        MessageSizeError: The Websocket payload is too large.
        InvalidAPIVersionError: If using incorrect API version.
        EventRateLimitError: If the API key has exceeded its daily event limit.
        IPRateLimitError: If the IP has exceeded its daily event limit.
        MissingAPIKeyError: If the API key is missing.
        InvalidAPIKeyError: If the API key is invalid.
        SDKError: If there is a non-specific error that is indicated by the server.
    """
    if message["status"] == "ok":
        return None  # This message does not contain an error
    elif message["reason"] == ErrorReason.MESSAGE_TOO_LARGE:
        raise MessageSizeError
    elif ErrorReason.API_KEY_INVALID.value in message["reason"]:
        raise InvalidAPIKeyError(message["reason"])
    elif ErrorReason.API_KEY_MISSING.value in message["reason"]:
        raise MissingAPIKeyError(message["reason"])
    else:
        raise SDKError(message["reason"])


def network_id_to_name(network_id: int):
    return {
        1: "main",
        3: "ropsten",
        4: "rinkeby",
        5: "goerli",
        42: "kovan",
        100: "xdai",
        56: "bsc",
    }[network_id]


def status_to_event_code(status: str):
    """
    Takes in the server status code ``status`` and returns the event code equivalent.
    """
    return {
        "sent": "txSent",
        "pending": "txPool",
        "pending-simulation": "txPoolSimulation",
        "stuck": "txStuck",
        "confirmed": "txConfirmed",
        "failed": "txFailed",
        "speedup": "txSpeedUp",
        "cancel": "txCancel",
        "dropped": "txDropped",
    }[status]


def is_server_echo(event_code: str):
    """Determines if the ``event_code`` is an echo response from the server.

    Args:
        event_code: The event code from the server message.

    Returns:
        True for if it is a server echo message, False otherwise.
    """
    return event_code in {
        "txRequest",
        "nsfFail",
        "txRepeat",
        "txAwaitingApproval",
        "txConfirmReminder",
        "txSendFail",
        "txError",
        "txUnderPriced",
        "txSent",
    }
