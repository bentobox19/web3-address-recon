import logging
import sqlite3
import threading

from src.config import config

logger = logging.getLogger(__name__)

class DBClient:
    _lock = threading.RLock()
    def __init__(self):
        logger.info(f"Initializing local DB at {config.SQLITE_DB_FILE}")

        self.conn = sqlite3.connect(config.SQLITE_DB_FILE)
        # Set the row_factory to return dictionary-like Row objects
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        # TODO
        # Field `safe_threshold` denormalized for perfomance.
        # Refactor to a separate 'safes' table if scaling requires.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS addresses (
                network TEXT,
                address TEXT,
                native_balance TEXT,
                is_eoa BOOLEAN,
                is_safe BOOLEAN,
                safe_threshold INTEGER,
                PRIMARY KEY (network, address)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS safe_owners (
                network TEXT,
                safe_address TEXT,
                owner_address TEXT,
                PRIMARY KEY (network, safe_address, owner_address),
                FOREIGN KEY (network, safe_address) REFERENCES addresses (network, address)
            )
        ''')
        self.conn.commit()

    def ensure_address_record(self, network: str, address: str):
        with self._lock:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO addresses (network, address)
                    VALUES (?, ?)
                    ON CONFLICT(network, address) DO NOTHING
                    """,
                    (network, address)
                )
                self.conn.commit()
            except sqlite3.Error as e:
                logger.error("Error ensuring address record exists: %s", e)

    def upsert_address_field(self, network: str, address: str, field_name: str, value):
        if field_name not in ['native_balance', 'is_eoa', 'is_safe', 'safe_threshold']:
            logger.error(f"Invalid field name: {field_name}")
            return

        with self._lock:
            try:
                self.ensure_address_record(network, address)

                query = f"UPDATE addresses SET {field_name} = ? WHERE network = ? AND address = ?"
                self.cursor.execute(
                    query,
                    (value, network, address)
                )
                self.conn.commit()
                logger.info(
                    f"Successfully upserted {field_name} for address {address} on network {network}"
                )
            except sqlite3.Error as e:
                logger.error(
                    f"Error upserting {field_name} for address {address} on network {network}: {e}"
                )

    def add_safe_owners(self, network: str, safe_address: str, owners: list[str]):
        with self._lock:
            try:
                for owner_address in owners:
                    self.ensure_address_record(network, owner_address)

                    self.cursor.execute(
                        """
                        INSERT INTO safe_owners (network, safe_address, owner_address)
                        VALUES (?, ?, ?)
                        ON CONFLICT(network, safe_address, owner_address) DO NOTHING
                        """,
                        (network, safe_address, owner_address)
                    )
                self.conn.commit()
            except sqlite3.Error as e:
                logger.error(f"Error adding safe owners for {safe_address}: {e}")

    def close(self):
        logger.info("Closing DB connection")
        self.conn.close()
