import logging
import dataclasses
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

@dataclasses.dataclass
class AddressRecord:
    network: str
    address: str
    native_balance: str = "0"
    is_eoa: bool | None = None
    is_safe: bool | None = None

class AddressAnalyzer:
    def __init__(self, db_client, rpc_client):
        self.db_client = db_client
        self.rpc_client = rpc_client

    def process(self, addresses):
        if not addresses:
            logger.info("No addresses to process.")
            return

        with ThreadPoolExecutor() as executor:
            future_to_address = {}
            for network, address in addresses:
                if network not in self.rpc_client.client_map:
                    logger.error(f"Unsupported network: {network}")
                    continue

                self.db_client.ensure_address_record(network, address)

                future_to_address[executor.submit(self._fetch_balance, network, address)] = (network, address)
                future_to_address[executor.submit(self._fetch_is_eoa, network, address)] = (network, address)
                future_to_address[executor.submit(self._fetch_is_safe, network, address)] = (network, address)

            for future in as_completed(future_to_address):
                network, address = future_to_address[future]
                try:
                    field_name, value = future.result()
                    if value is not None:
                        self.db_client.upsert_address_field(network, address, field_name, value)

                        if field_name == 'is_safe' and value is True:
                            future_to_address[executor.submit(self._fetch_safe_owners, network, address)] = (network, address)
                            future_to_address[executor.submit(self._fetch_safe_threshold, network, address)] = (network, address)
                        elif field_name == 'safe_owners':
                            self.db_client.add_safe_owners(network, address, value)

                except Exception as exc:
                    logger.error(f'{network}:{address} generated an exception: {exc}')

        self.db_client.close()

    def _fetch_balance(self, network: str, address: str):
        native_balance = self.rpc_client.get_native_balance(network, address)
        logger.debug(f"Native balance - {network}:{address} - {native_balance}")
        return 'native_balance', native_balance

    def _fetch_is_eoa(self, network: str, address: str):
         is_eoa = self.rpc_client.is_eoa(network, address)
         logger.debug(f"Is EOA - {network}:{address} - {is_eoa}")
         return 'is_eoa', is_eoa

    def _fetch_is_safe(self, network: str, address: str):
        is_safe = self.rpc_client.is_safe(network, address)
        logger.debug(f"Is Safe - {network}:{address} - {is_safe}")
        return 'is_safe', is_safe

    def _fetch_safe_owners(self, network: str, address: str):
        safe_owners = self.rpc_client.get_safe_owners(network, address)
        logger.debug(f"Safe Owners - {network}:{address} - {safe_owners}")
        return 'safe_owners', safe_owners

    def _fetch_safe_threshold(self, network: str, address: str):
        safe_threshold = self.rpc_client.get_safe_threshold(network, address)
        logger.debug(f"Safe Threshold - {network}:{address} - {safe_threshold}")
        return 'safe_threshold', safe_threshold
