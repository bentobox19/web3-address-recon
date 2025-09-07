import aiosql
import aiosqlite
import asyncio
import logging
import os
from typing import Dict, Any, List

from src.config import config

logger = logging.getLogger(__name__)

class DBClient:
    def __init__(self):
        self._db_file = config.SQLITE_DB_FILE
        current_dir = os.path.dirname(os.path.abspath(__file__))
        queries_sql_file_path = os.path.join(current_dir, "queries.sql")
        self._queries = aiosql.from_path(queries_sql_file_path, "aiosqlite")
        self._conn = None

    async def connect(self):
        if self._conn:
            return
        self._conn = await aiosqlite.connect(self._db_file)
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.commit()
        await self._initialize_schema()

    async def _initialize_schema(self):
        logger.info(f"Initializing async local DB at {self._db_file}")
        await self._queries.create_addresses_table(self._conn)
        await self._queries.create_evm_properties_table(self._conn)
        await self._queries.create_safe_wallets_table(self._conn)
        await self._queries.create_safe_wallet_owners_table(self._conn)
        await self._conn.commit()

    async def add_address(self, network: str, address: str, source: str) -> int:
        result = await self._queries.insert_address(self._conn,
            network=network,
            address=address,
            source=source
        )
        await self._conn.commit()

        return result[0][0] if result else None

    async def save_evm_properties(self, address_id: int, properties: Dict[str, Any]):
        await self._queries.upsert_evm_properties(
            self._conn,
            address_id=address_id,
            native_balance=properties.get('native_balance'),
            is_eoa=properties.get('is_eoa'),
            is_safe=properties.get('is_safe'),
        )
        await self._conn.commit()

    async def save_safe_wallet_data(self, safe_address_id: int, owners: List[str], safe_wallet_data: Dict[str, Any]):
        await self._queries.upsert_safe_wallet(
            self._conn,
            address_id=safe_address_id,
            threshold=safe_wallet_data.get('threshold'),
            nonce=safe_wallet_data.get('nonce'),
            owner_count=len(owners) if owners else None
        )

        for owner in owners:
            await self._queries.insert_safe_wallet_owner(
                self._conn,
                safe_address_id=safe_address_id,
                owner_address=owner
            )

        await self._conn.commit()

    async def close(self):
        if self._conn:
            logger.info("Closing DB connection")
            await self._conn.close()
