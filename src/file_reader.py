import logging

from src.config import config

logger = logging.getLogger(__name__)

class FileReader:
    def get_addresses(self):
        if not config.args or not hasattr(config.args, 'input_file'):
            return []

        try:
            with open(config.args.input_file, 'r') as f:
                logger.info(f"Reading {config.args.input_file}")
                lines = [line.strip() for line in f if line.strip()]
                parsed_data = []
                for i, line in enumerate(lines):
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        network, address = parts
                        parsed_data.append((network.lower(), address.lower()))
                    else:
                        logger.warning(f"Skipping malformed line at index {i}: '{line}'")

                logger.info(f"Read {len(parsed_data)} addresses")
                return parsed_data
        except FileNotFoundError:
            print(f"Error: The file '{config.args.input_file}' was not found.")
            return []
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
            return []
