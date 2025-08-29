import logging
import requests

from functools import wraps
from ratelimit import limits, sleep_and_retry
from requests.exceptions import RequestException

from src.config import config
from .base import RPCClientBase

logger = logging.getLogger(__name__)

def alchemy_request(json_rpc_method, params_builder=None):
    def decorator(func):
        @wraps(func)
        @sleep_and_retry
        @limits(calls=300, period=1)
        def wrapper(self, network: str, address: str, *args, **kwargs):
            if network not in self.base_urls:
                logger.debug("Unsupported network: %s", network)
                # Pass None to the decorated function to handle default/error case
                return func(self, network, address, None, *args, **kwargs)

            try:
                url = self.base_urls[network]
                params = params_builder(address) if params_builder else [address, "latest"]
                payload = {
                    "jsonrpc": "2.0",
                    "method": json_rpc_method,
                    "params": params,
                    "id": 1
                }
                response = requests.post(url, json=payload, timeout=10)
                response.raise_for_status()
                result = response.json().get("result")
                return func(self, network, address, result, *args, **kwargs)

            except RequestException as e:
                logger.error(f"Network error during {json_rpc_method} for {address} on {network}: {e}")
                return func(self, network, address, None, *args, **kwargs)
            except (ValueError, KeyError) as e:
                logger.error(f"API response parsing error during {json_rpc_method} for {address} on {network}: {e}")
                return func(self, network, address, None, *args, **kwargs)
        return wrapper
    return decorator

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
