import logging
import requests

from ratelimit import limits, sleep_and_retry
from requests.exceptions import RequestException
from src.config import config
from .base import RPCClientBase

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

    @sleep_and_retry
    @limits(calls=300, period=1)
    def get_native_balance(self, network: str, address: str) -> str:
        if network not in self.base_urls:
            logger.error("Unsupported network: %s", network)
            return "0"

        try:
            url = self.base_urls[network]
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [address, "latest"],
                "id": 1
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json().get("result")
            if result:
                balance_wei = int(result, 16)
                return str(balance_wei)

            return "0"

        except RequestException as e:
            logger.error("Network error getting balance for address %s on network %s: %s", address, network, e)
            return "0"
        except (ValueError, KeyError) as e:
            logger.error("API response parsing error for address %s on network %s: %s", address, network, e)
            return "0"

    @sleep_and_retry
    @limits(calls=300, period=1)
    def is_eoa(self, network: str, address: str) -> bool | None:
        if network not in self.base_urls:
            logger.debug("Unsupported network: %s", network)
            return None

        try:
            url = self.base_urls[network]
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getCode",
                "params": [address, "latest"],
                "id": 1
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json().get("result")
            if result:
                return result == '0x'

            return None

        except RequestException as e:
            logger.error("Network error getting code for address %s on network %s: %s", address, network, e)
            return None
        except (ValueError, KeyError) as e:
            logger.error("API response parsing error for address %s on network %s: %s", address, network, e)
            return None

    @sleep_and_retry
    @limits(calls=300, period=1)
    def is_safe(self, network: str, address: str) -> bool | None:
        if network not in self.base_urls:
            logger.debug("Unsupported network: %s", network)
            return None

        try:
            url = self.base_urls[network]
            # Check for masterCopy() method, a good indicator of a Gnosis Safe proxy
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [{"to": address, "data": "0xa619486e"}, "latest"],
                "id": 1
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json().get("result")
            return result is not None and result != '0x'

        except RequestException as e:
            logger.error("Network error checking if address %s is a safe on network %s: %s", address, network, e)
            return None
        except (ValueError, KeyError) as e:
            logger.error("API response parsing error for address %s on network %s: %s", address, network, e)
            return None

    @sleep_and_retry
    @limits(calls=300, period=1)
    def get_safe_owners(self, network: str, address: str) -> list[str] | None:
        if network not in self.base_urls:
            logger.debug("Unsupported network: %s", network)
            return None

        try:
            url = self.base_urls[network]
            # Corresponds to getOwners() method
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [{"to": address, "data": "0xa0e67e2b"}, "latest"],
                "id": 1
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json().get("result")
            if result and result != '0x':
                # The result is a single hex string, we need to split it into 32-byte chunks (addresses)
                # First 32 bytes are the offset, next 32 bytes are the length, then the addresses
                owners_data = result[2:] # remove 0x
                owner_chunks = [owners_data[i:i+64] for i in range(128, len(owners_data), 64)]
                return [f"0x{chunk[24:]}" for chunk in owner_chunks]
            return []
        except Exception as e:
            logger.error(f"Error getting Gnosis Safe owners {e}")
            return None

    @sleep_and_retry
    @limits(calls=300, period=1)
    def get_safe_threshold(self, network: str, address: str) -> int | None:
        if network not in self.base_urls:
            logger.debug("Unsupported network: %s", network)
            return None
        try:
            url = self.base_urls[network]
            # Corresponds to getThreshold() method
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [{"to": address, "data": "0xe75235b8"}, "latest"],
                "id": 1
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json().get("result")
            if result and result != '0x':
                return int(result, 16)
            return None
        except Exception as e:
            logger.error(f"Error getting Gnosis Safe threshold {e}")
            return None
