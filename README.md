# Web3 Address Recon

This tool processes a list of Web3 addresses from a TXT file, fetches information using Alchemy API, stores it in SQLite, and avoids redundant API calls by checking the database first.

<!-- MarkdownTOC -->

- Requirements
- Setup
    - RPC API Key
    - Database Management
    - Dependencies
- Usage
    - Input Format
- Features
- Potential Missing Features

<!-- /MarkdownTOC -->

## Requirements

- Python 3.11+
- `uv`

## Setup

### RPC API Key

We are using [Alchemy](http://alchemy.com/):

Copy `.env-sample` into `.env `. Replace with _your_ API Key.

```bash
export ALCHEMY_API_KEY=9yUn7YrS814EkZ-2xI0Ex0VFHcPAUmRw
```

### Database Management

- Export: `sqlite3 ./db/web3-address-recon.sqlite3 .dump > dump.sql`
- Import: `sqlite3 ./db/web3-address-recon.sqlite3 < dump.sql`

Modify the location of this file at the `.env` file

```bash
export SQLITE_DB_FILE=./db/web3-address-recon.sqlite3
```

### Dependencies

```bash
# First time
uv venv
uv pip install -r requirements.txt
```

## Usage

```bash
uv run python web3_address_recon.py -f $YOUR_TXT_WITH_WEB3_ADDRESSES
```

### Input Format

TXT file with lines like:

```
Ethereum 0x56e47B113E9n1cAfDne177n8c74c51DnB0F55553n62d8
Polygon 0xa1eDedeF63bnef0ean2d2D0n71bnnDF88F715n43ec4fE
```

## Features

- Checks if EOA or contract
- Detects if Gnosis Safe
- For Safe: owners, threshold, version
- Native balance, nonce
- Balances in specified tokens (network-specific)
- Latest asset transfers (up to 10)

## Potential Missing Features

- ENS resolution (Ethereum)
- NFT holdings
- Flag to force update in the local DB
- Export of the DB to CSV/JSON.
