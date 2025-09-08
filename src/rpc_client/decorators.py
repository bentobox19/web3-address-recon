import logging
from functools import wraps

import httpx
from aiolimiter import AsyncLimiter

logger = logging.getLogger(__name__)

def alchemy_request(json_rpc_method, params_builder=None):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, network: str, address: str, *args, **kwargs):
            if network not in self.base_urls:
                logger.debug("Unsupported network: %s", network)
                return func(self, network, address, None, *args, **kwargs)

            url = self.base_urls[network]
            params = params_builder(address) if params_builder else [address, "latest"]
            payload = {
                "jsonrpc": "2.0",
                "method": json_rpc_method,
                "params": params,
                "id": 1
            }

            try:
                # rate-limit and optionally bound concurrency
                async with self._alchemy_rate_limit:
                    async with self._alchemy_concurrency:
                        resp = await self._http.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                result = data.get("result")
                return func(self, network, address, result, *args, **kwargs)

            except httpx.HTTPError as e:
                logger.error("Network error during %s for %s on %s: %s",
                             json_rpc_method, address, network, e)
                return func(self, network, address, None, *args, **kwargs)
            except (ValueError, KeyError) as e:
                logger.error("API response parsing error during %s for %s on %s: %s",
                             json_rpc_method, address, network, e)
                return func(self, network, address, None, *args, **kwargs)
        return wrapper
    return decorator
