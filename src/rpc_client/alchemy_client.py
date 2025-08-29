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

    # Check for masterCopy() (method signature 0xa619486e), a good indicator of a Gnosis Safe proxy
    @alchemy_request("eth_call", params_builder=lambda addr: [{"to": addr, "data": "0xa619486e"}, "latest"])
    def is_safe(self, network: str, address: str, result: str | None) -> bool | None:
        return result is not None and result != '0x'

    # Check for getThreshold() (method signature 0xe75235b8)
    @alchemy_request("eth_call", params_builder=lambda addr: [{"to": addr, "data": "0xe75235b8"}, "latest"])
    def get_safe_threshold(self, network: str, address: str, result: str | None) -> int | None:
        if result and result != '0x':
            return int(result, 16)
        return None

    # Check for nonce() (method signature 0xaffed0e0)
    @alchemy_request("eth_call", params_builder=lambda addr: [{"to": addr, "data": "0xaffed0e0"}, "latest"])
    def get_safe_nonce(self, network: str, address: str, result: str | None) -> int | None:
        if result and result != '0x':
            return int(result, 16)
        return None

    # Check for getOwners(method signature 0xa0e67e2b)
    @alchemy_request("eth_call", params_builder=lambda addr: [{"to": addr, "data": "0xa0e67e2b"}, "latest"])
    def get_safe_owners(self, network: str, address: str, result: str | None) -> list[str] | None:
        if result and result != '0x':
            # The result of this call is a hex string of tightly packed addresses.
            # We skip first the '0x' prefix (2) + 128 hex chars: offset (64) + array length (64)
            raw_owners = result[130:]
            owners = []
            for i in range(0, len(raw_owners), 64):
                padded_addr = raw_owners[i:i+64]
                addr_hex = padded_addr[24:64] # The actual address hex (last 40 chars)
                owners.append(f"0x{addr_hex}")
            return owners
        return None
