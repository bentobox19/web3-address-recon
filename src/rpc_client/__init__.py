import logging
from functools import wraps

from .base import RPCClientBase
from .alchemy_client import AlchemyClient

logger = logging.getLogger(__name__)

def client_checker(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        network = args[0] if args else kwargs.get('network')
        if not network:
            logger.error("Network argument not found.")
            return None

        if (client := self.client_map.get(network)):
            new_args = (self, client) + args
            return func(*new_args, **kwargs)

        logger.warning(f"No RPC client configured for network: {network}")

        if func.__name__ == 'get_native_balance':
            return 0.0
        elif func.__name__ == 'is_eoa':
            return None
        return None
    return wrapper

class RPCClient(RPCClientBase):
    def __init__(self):
        self.alchemy_client = AlchemyClient()

        self.client_map = {
            "arbitrum": self.alchemy_client,
            "avalanche": self.alchemy_client,
            "base": self.alchemy_client,
            "bsc": self.alchemy_client,
            "ethereum": self.alchemy_client,
            "linea": self.alchemy_client,
            "optimism": self.alchemy_client,
            "polygon": self.alchemy_client,
            "sei": self.alchemy_client,
            "zksync": self.alchemy_client,
        }

    @client_checker
    def get_native_balance(self, client, network: str, address: str) -> float:
        return client.get_native_balance(network, address)

    @client_checker
    def is_eoa(self, client, network: str, address: str) -> bool | None:
        return client.is_eoa(network, address)
