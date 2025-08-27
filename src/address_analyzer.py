import logging
import dataclasses

logger = logging.getLogger(__name__)

@dataclasses.dataclass
class AddressRecord:
    network: str
    address: str
    native_balance: str = "0"
    is_eoa: bool | None = None

class AddressAnalyzer:
    def __init__(self, db_client, alchemy_client):
        self.db_client = db_client
        self.alchemy_client = alchemy_client

    def process(self, addresses):
        if not addresses:
            logger.info("No addresses to process.")
            return

        # TODO
        # Eventually, we want to parallelize the requests to N threads
        for network, address in addresses:
            record = {}
            # Create a dataclass instance in memory for this address
            record = (AddressRecord(
                network=network,
                address=address,
                native_balance="0"
            ))

            # Retrieve record from the database
            db_record = self.db_client.get_address_record(network, address)

            if db_record:
                logger.debug(f"Found existing record for {address} on {network}")
                # Update dataclass instance with data from the database
                record.native_balance = db_record.get('native_balance', record.native_balance)
                record.is_eoa = db_record.get('is_eoa', record.is_eoa)

                print(f"Native Balance: {record.native_balance}, EOA: {record.is_eoa}")

            # Get native balance
            native_balance = self.alchemy_client.get_native_balance(network, address)
            logger.debug(f"Native balance - {network}:{address} - {native_balance}")

            # Update the in-memory dictionary with the new data
            record.native_balance = native_balance

            is_eoa = self.alchemy_client.is_eoa(network, address)
            logger.debug(f"Is EOA - {network}:{address} - {is_eoa}")
            record.is_eoa = is_eoa

            # Send the updated object to the database
            self.db_client.upsert_address_record(record)
