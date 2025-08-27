import logging
import sqlite3

from src.config import config

logger = logging.getLogger(__name__)

class DBClient:
    def __init__(self):
        logger.info(f"Initializing local DB at {config.SQLITE_DB_FILE}")

        self.conn = sqlite3.connect(config.SQLITE_DB_FILE)
        # Set the row_factory to return dictionary-like Row objects
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS addresses (
                network TEXT,
                address TEXT,
                native_balance TEXT,
                is_eoa BOOLEAN,
                PRIMARY KEY (network, address)
            )
        ''')
        self.conn.commit()

    def get_address_record(self, network: str, address: str) -> dict | None:
        try:
            self.cursor.execute(
                "SELECT * FROM addresses WHERE network = ? AND address = ?",
                (network, address)
            )
            record = self.cursor.fetchone()
            if record:
                # Convert the Row object to a standard dictionary
                return dict(record)
            else:
                return None
        except sqlite3.Error as e:
            logger.error("Error retrieving address record: %s", e)
            return None

    def upsert_address_record(self, record: dict):
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO addresses (network, address, native_balance, is_eoa) VALUES (?, ?, ?, ?)",
                (record.network, record.address, record.native_balance, record.is_eoa)
            )

            self.conn.commit()
            logger.info("Successfully upserted record for address %s on network %s",
                        record.address, record.network)
        except sqlite3.Error as e:
            logger.error("Error upserting address record: %s", e)
