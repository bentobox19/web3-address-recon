import asyncio
import logging
import sys

from src.address_analyzer import AddressAnalyzer
from src.config import config
from src.db_client import DBClient
from src.file_reader import FileReader
from src.rpc_client import RPCClient

async def main():
    if not config.args:
        return

    config.setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Web3 Address Reconnaissance Tool")

    db_client = DBClient()
    rpc_client = RPCClient()
    file_reader = FileReader()
    address_analyzer = AddressAnalyzer(db_client, rpc_client)

    try:
        await db_client.connect()
        addresses = file_reader.get_addresses()
        await address_analyzer.process(addresses)

    except asyncio.CancelledError:
        logger.info("Main task was cancelled, shutting down.")

    except Exception as e:
        logger.error(f"An unhandled error occurred: {e}", exc_info=True)

    finally:
        await db_client.close()

if __name__ == "__main__":
    asyncio.run(main())
