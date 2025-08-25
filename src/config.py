import argparse
import logging
import os
import sys

from dotenv import load_dotenv

class Config:
    """
    A singleton-like class for managing application configuration, environment
    variables, command-line arguments, and logging setup.
    """
    def __init__(self):
        self._load_envs()
        self._parser = self._create_parser()
        self.args = self._parse_args()

    def setup_logging(self):
        log_level = self.args.log_level.upper()
        logging.basicConfig(
            format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=log_level
        )

    def _load_envs(self):
        load_dotenv()
        self.ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")
        if not self.ALCHEMY_API_KEY:
          raise ValueError("ALCHEMY_API_KEY environment variable not set.")

        self.SQLITE_DB_FILE = os.getenv("SQLITE_DB_FILE") or "./db/web3-address-recon.sqlite3"

    def _create_parser(self):
        parser = argparse.ArgumentParser(description="Web3 Address Reconnaissance Tool")
        parser.add_argument(
            '-f', '--file',
            dest='input_file',
            type=str,
            required=True,
            help="Path to the input TXT file")
        parser.add_argument(
            '-l', '--log-level',
            dest='log_level',
            type=str,
            default='ERROR',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            help="Set the logging level"
        )
        return parser

    def _parse_args(self):
        if len(sys.argv) > 1:
            try:
                return self._parser.parse_args()
            except SystemExit:
                return None
        else:
            self._parser.print_help()
            return None

# Global instance of Config for easy access
config = Config()
