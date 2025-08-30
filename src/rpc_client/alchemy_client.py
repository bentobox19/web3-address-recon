import logging

from src.config import config
from .base import RPCClientBase
from .decorators import alchemy_request

logger = logging.getLogger(__name__)

class AlchemyClient(RPCClientBase):
    def __init__(self):
        logger.info("Initializing Alchemy Client")

        self.base_urls = {
            "arbitrum": f"https://arb-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            "avalanche": f"https://avax-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            "base": f"https://base-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            "bsc": f"https://bnb-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            "ethereum": f"https://eth-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            "linea": f"https://linea-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            "optimism": f"https://opt-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            "polygon": f"https://polygon-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            "sei": f"https://sei-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            "zksync": f"https://zksync-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}"
        }

    @alchemy_request("eth_getBalance")
    def get_native_balance(self, network: str, address: str, result: str | None) -> str:
        if result:
            return str(int(result, 16))
        return "0"

    @alchemy_request("eth_getCode")
    def is_eoa(self, network: str, address: str, result: str | None) -> bool | None:
        if result:
            return result == '0x'
        return None

    # Check for masterCopy() method (0xa619486e), a good indicator of a Gnosis Safe proxy
    @alchemy_request("eth_call", params_builder=lambda addr: [{"to": addr, "data": "0xa619486e"}, "latest"])
    def is_safe(self, network: str, address: str, result: str | None) -> bool | None:
        return result is not None and result != '0x'
