import asyncio
import logging
from typing import List, Tuple, Set

from src.config import config

logger = logging.getLogger(__name__)

class AddressAnalyzer:
    def __init__(self, db_client, rpc_client):
        self.db_client = db_client
        self.rpc_client = rpc_client
        self.queue = asyncio.Queue()

    async def process(self, addresses: List[Tuple[str, str]]):
        if not addresses:
            logger.info("No addresses to process.")
            return

        workers = [
            asyncio.create_task(self._worker(f'worker-{i}'))
            for i in range(config.args.workers)
        ]

        for network, address in addresses:
            if network in self.rpc_client.client_map:
                await self.queue.put((network, address, 'input-list'))
            else:
                logger.error(f"Unsupported network: {network}")

        await self.queue.join()

        for w in workers:
            w.cancel()
        await asyncio.gather(*workers, return_exceptions=True)

    async def _worker(self, name: str):
        while True:
            try:
                network, address, source = await self.queue.get()
                logger.info(f"[{name}] Processing: {network}:{address}")
                await self._analyze_address(network, address, source)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in {name}: {e}", exc_info=True)
            finally:
                self.queue.task_done()

    async def _analyze_address(self, network: str, address: str, source: str):
        address_id = await self.db_client.add_address(network, address, source)
        logger.info(f"Added address {network}:{address}. {address_id}")

        is_safe = await self._process_evm_properties(address_id, network, address)
        if is_safe:
            await self._process_safe_details(address_id, network, address)

    async def _process_evm_properties(self, address_id: int, network: str, address: str) -> bool:
        logger.debug(f"Request EVM properties for {address_id} - {network}:{address}")
        balance_task = self.rpc_client.get_native_balance(network, address)
        is_eoa_task = self.rpc_client.is_eoa(network, address)
        is_safe_task = self.rpc_client.is_safe(network, address)

        balance, is_eoa, is_safe = await asyncio.gather(
            balance_task, is_eoa_task, is_safe_task
        )

        evm_props = {
            "native_balance": balance,
            "is_eoa": is_eoa,
            "is_safe": is_safe,
        }
        logger.info(f"EVM properties from {address_id} - {network}:{address} - {evm_props}")
        await self.db_client.save_evm_properties(address_id, evm_props)

        return is_safe

    async def _process_safe_details(self, address_id: int, network: str, address: str):
        logger.debug(f"Request safe details for {address_id} - {network}:{address}")
        threshold_task = self.rpc_client.get_safe_threshold(network, address)
        nonce_task = self.rpc_client.get_safe_nonce(network, address)
        owners_task = self.rpc_client.get_safe_owners(network, address)

        threshold, nonce, owners = await asyncio.gather(
            threshold_task, nonce_task, owners_task
        )

        safe_wallet_data = {
            "network": network,
            "threshold": threshold,
            "nonce": nonce,
        }

        logger.info(f"Safe details from {address_id} - {network}:{address} {safe_wallet_data}")
        await self.db_client.save_safe_wallet_data(address_id, owners, safe_wallet_data)
