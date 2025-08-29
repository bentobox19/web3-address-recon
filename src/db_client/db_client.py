import aiosql
import aiosqlite
import asyncio
import logging
import os

from src.config import config
from .decorators import locked

logger = logging.getLogger(__name__)

class DBClient:
    def __init__(self):
        self._db_file = config.SQLITE_DB_FILE
        current_dir = os.path.dirname(os.path.abspath(__file__))
        queries_sql_file_path = os.path.join(current_dir, "queries.sql")
        self._queries = aiosql.from_path(queries_sql_file_path, "aiosqlite")
        self._conn = None
        self._lock = asyncio.Lock()

    async def connect(self):
        if self._conn:
            return
        self._conn = await aiosqlite.connect(self._db_file)
        await self._conn.execute("PRAGMA journal_mode=DELETE")
        await self._conn.commit()
        await self._initialize_schema()

    @locked("_lock")
    async def _initialize_schema(self):
        logger.info(f"Initializing async local DB at {self._db_file}")
        await self._queries.create_addresses_table(self._conn)
        await self._queries.create_safe_owners_table(self._conn)
        await self._conn.commit()

    @locked("_lock")
    async def ensure_address_record(self, network: str, address: str):
        await self._queries.insert_into_addresses(
            self._conn,
            network=network,
            address=address
        )
        await self._conn.commit()

    @locked("_lock")
    async def upsert_address_field(self, network: str, address: str, field_name: str, value):
        query_map = {
            'native_balance': self._queries.update_native_balance,
            'is_eoa': self._queries.update_is_eoa,
            'is_safe': self._queries.update_is_safe,
            'safe_threshold': self._queries.update_safe_threshold,
            'safe_nonce': self._queries.update_safe_nonce,
            'safe_owner_count': self._queries.update_safe_owner_count,
        }
        query_func = query_map.get(field_name)

        if not query_func:
            logger.error(f"Invalid field name: {field_name}")
            return

        await query_func(
            self._conn,
            value=value,
            network=network,
            address=address
        )
        await self._conn.commit()

    @locked("_lock")
    async def add_safe_owners(self, network: str, safe_address: str, owners: list):
        for owner_address in owners:
            await self._queries.insert_into_safe_owners(
                self._conn,
                network=network,
                safe_address=safe_address,
                owner_address=owner_address
            )
        await self._conn.commit()

    async def close(self):
        if self._conn:
            logger.info("Closing DB connection")
            await self._conn.close()
