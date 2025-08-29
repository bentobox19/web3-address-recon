import asyncio
import logging

from typing import List, Tuple

from src.config import config

logger = logging.getLogger(__name__)

class AddressAnalyzer:
    def __init__(self, db_client, rpc_client):
        self.db_client = db_client
        self.rpc_client = rpc_client
        self.queue = asyncio.Queue()

    async def process(self, addresses: List[Tuple[str, str]], num_workers:int = config.args.workers):
        if not addresses:
            logger.info("No addresses to process.")
            return

        ensure_tasks = [
            self.db_client.ensure_address_record(network, address)
            for network, address in addresses
            if network in self.rpc_client.client_map
        ]
        await asyncio.gather(*ensure_tasks)
        logger.info("Ensured all listed addresses are in the database")

        workers = [
            asyncio.create_task(self._worker(f'worker-{i}'))
            for i in range(num_workers)
        ]

        try:
            for network, address in addresses:
                if network not in self.rpc_client.client_map:
                    logger.error(f"Unsupported network: {network}")
                    continue
                await self.queue.put(('initial_check', network, address))
            await self.queue.join()

        finally:
            for w in workers:
                w.cancel()
            await asyncio.gather(*workers, return_exceptions=True)

    async def _worker(self, name: str):
        while True:
            try:
                task_type, network, address = await self.queue.get()

                if task_type == 'initial_check':
                    await self.queue.put(('fetch_balance', network, address))
                    await self.queue.put(('fetch_is_eoa', network, address))
                    await self.queue.put(('fetch_is_safe', network, address))

                elif task_type == 'fetch_balance':
                    field, value = await self._fetch_balance(network, address)
                    await self.db_client.upsert_address_field(network, address, field, value)

                elif task_type == 'fetch_is_eoa':
                    field, value = await self._fetch_is_eoa(network, address)
                    await self.db_client.upsert_address_field(network, address, field, value)

                elif task_type == 'fetch_is_safe':
                    field, value = await self._fetch_is_safe(network, address)
                    await self.db_client.upsert_address_field(network, address, field, value)
                    # If it's a safe, produce new dependent tasks
                    if value is True:
                        await self.queue.put(('fetch_safe_threshold', network, address))
                        await self.queue.put(('fetch_safe_nonce', network, address))
                        await self.queue.put(('fetch_safe_owners', network, address))

                elif task_type == 'fetch_safe_threshold':
                    field, value = await self._fetch_safe_threshold(network, address)
                    await self.db_client.upsert_address_field(network, address, field, value)

                elif task_type == 'fetch_safe_nonce':
                    field, value = await self._fetch_safe_nonce(network, address)
                    await self.db_client.upsert_address_field(network, address, field, value)

                elif task_type == 'fetch_safe_owners':
                    field, owners = await self._fetch_safe_owners(network, address)
                    if owners:
                        await self.db_client.upsert_address_field(network, address, 'safe_owner_count', len(owners))
                        await self.db_client.add_safe_owners(network, address, owners)
                        # TODO
                        # The owners we discover are record into our addresses database
                        # for further processing.
                        # We want to have some additional flags to show why we included them,
                        # and some controls to avoid infinite loops (e.g. A -> B -> C -> A).
                        # for owner_address in owners:
                        #     await self.db_client.ensure_address_record(
                        #         network,
                        #         owner_address
                        #     )
                        #     await self.queue.put(('initial_check', network, owner_address))

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in {name}: {e}", exc_info=True)
            finally:
                self.queue.task_done()

    async def _fetch_balance(self, network: str, address: str):
        balance = await self.rpc_client.get_native_balance(network, address)
        logger.debug(f"Retrieved native balance - {network}:{address} - {balance}")
        return 'native_balance', balance

    async def _fetch_is_eoa(self, network: str, address: str):
        is_eoa = await self.rpc_client.is_eoa(network, address)
        logger.debug(f"Retrieved EOA status - {network}:{address} - {is_eoa}")
        return 'is_eoa', is_eoa

    async def _fetch_is_safe(self, network: str, address: str):
        is_safe = await self.rpc_client.is_safe(network, address)
        logger.debug(f"Retrieved Safe wallet status - {network}:{address} - {is_safe}")
        return 'is_safe', is_safe

    async def _fetch_safe_threshold(self, network: str, address: str):
        threshold = await self.rpc_client.get_safe_threshold(network, address)
        logger.debug(f"Retrieved Safe threshold - {network}:{address} - {threshold}")
        return 'safe_threshold', threshold

    async def _fetch_safe_nonce(self, network: str, address: str):
        nonce = await self.rpc_client.get_safe_nonce(network, address)
        logger.debug(f"Retrieved Safe nonce - {network}:{address} - {nonce}")
        return 'safe_nonce', nonce

    async def _fetch_safe_owners(self, network: str, address: str):
        owners = await self.rpc_client.get_safe_owners(network, address)
        logger.debug(f"Retrieved Safe Owners - {network}:{address} - {owners}")
        return 'safe_owners', owners
