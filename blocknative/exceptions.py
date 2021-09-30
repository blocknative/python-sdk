"""Error classes for all possible exceptions.
"""
class SDKError(Exception):
    """Base class for Blocknative sdk errors"""


# SDK handled errors
class WebsocketRateLimitError(SDKError):
    """Raised when number of ws messages has exceeded limit within a given duration"""


class MessageSizeError(SDKError):
    """Raised when the Websocket payload is too large"""


class InvalidAPIVersionError(SDKError):
    """Raised when using incorrect API version."""


# User handled errors
class EventRateLimitError(SDKError):
    """Raised when API key has exceeded its daily event limit"""


class SimulatedEventRateLimitError(SDKError):
    """Raised when API key has exceeded its daily simulated event limit"""


class IPRateLimitError(SDKError):
    """Raised when IP has exceeded its daily event limit"""


class MissingAPIKeyError(SDKError):
    """Raised when the API key is missing"""


class InvalidAPIKeyError(SDKError):
    """Raised when the API key is invalid"""
