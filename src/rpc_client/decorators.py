import requests

from functools import wraps
from ratelimit import limits, sleep_and_retry
from requests.exceptions import RequestException

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
