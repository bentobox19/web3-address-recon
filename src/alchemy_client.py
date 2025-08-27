import logging
import requests

from ratelimit import limits, sleep_and_retry
from requests.exceptions import RequestException
from src.config import config

logger = logging.getLogger(__name__)

class AlchemyClient:
    def __init__(self):
        logger.info("Initializing Alchemy Client")

        self.base_urls = {
            "arbitrum": f"https://arb-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            "avalanche": f"https://avax-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            "base": f"https://base-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            # "bitcoin": f"",
            "bsc": f"https://bnb-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            "ethereum": f"https://eth-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            # "fli": f"",
            "linea": f"https://linea-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            "optimism": f"https://opt-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            "polygon": f"https://polygon-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            "sei": f"https://sei-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}",
            # "solana": f"",
            "zksync": f"https://zksync-mainnet.g.alchemy.com/v2/{config.ALCHEMY_API_KEY}"
        }

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
    def get_native_balance(self, network: str, address: str) -> str:
        # Check if the requested network is supported.
        if network not in self.base_urls:
            logger.debug("Unsupported network: %s", network)
            return "0"

        # TODO
        # Interact with non-EVM networks
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
