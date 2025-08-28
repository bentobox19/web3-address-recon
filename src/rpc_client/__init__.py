import logging

from .base import RPCClientBase
from .alchemy_client import AlchemyClient

logger = logging.getLogger(__name__)

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

    def get_native_balance(self, network: str, address: str) -> float:
        if (client := self.client_map.get(network)):
            return client.get_native_balance(network, address)

        logger.warning(f"No RPC client configured for network: {network}")
        return 0.0

    def is_eoa(self, network: str, address: str) -> bool | None:
        if (client := self.client_map.get(network)):
            return client.is_eoa(network, address)

        logger.warning(f"No RPC client configured for network: {network}")
        return None
