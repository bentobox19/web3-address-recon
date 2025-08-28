import logging

from src.config import config
from src.file_reader import FileReader
from src.db_client import DBClient
from src.rpc_client import RPCClient
from src.address_analyzer import AddressAnalyzer

def main():
    if not config.args:
        return

    config.setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Web3 Address Reconnaissance Tool")

    # Setup tool modules
    db_client = DBClient()
    rpc_client = RPCClient()
    file_reader = FileReader()
    address_analyzer = AddressAnalyzer(db_client, rpc_client)

    # Engage on the main task
    addresses = file_reader.get_addresses()
    address_analyzer.process(addresses)

if __name__ == "__main__":
    main()
