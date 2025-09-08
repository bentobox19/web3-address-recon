-- name: create_addresses_table!
CREATE TABLE IF NOT EXISTS addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    network TEXT NOT NULL,
    address TEXT NOT NULL,
    source TEXT NOT NULL,
    UNIQUE (network, address)
);

-- name: create_evm_properties_table!
CREATE TABLE IF NOT EXISTS evm_properties (
    address_id INTEGER PRIMARY KEY,
    native_balance TEXT,
    is_eoa BOOLEAN,
    is_safe BOOLEAN,
    FOREIGN KEY (address_id) REFERENCES addresses (id)
);

-- name: create_safe_wallets_table!
CREATE TABLE IF NOT EXISTS safe_wallets (
    address_id INTEGER PRIMARY KEY,
    threshold INTEGER,
    nonce INTEGER,
    owner_count INTEGER,
    FOREIGN KEY (address_id) REFERENCES addresses (id)
);

-- name: create_safe_wallet_owners_table!
CREATE TABLE IF NOT EXISTS safe_wallet_owners (
    safe_address_id INTEGER NOT NULL,
    owner_address TEXT NOT NULL,
    PRIMARY KEY (safe_address_id, owner_address),
    FOREIGN KEY (safe_address_id) REFERENCES addresses (id)
);

-- name: insert_address
INSERT INTO addresses (network, address, source)
VALUES (:network, :address, :source)
ON CONFLICT(network, address) DO NOTHING
RETURNING id;

-- name: get_address_id^
SELECT id FROM addresses WHERE network = :network AND address = :address;

-- name: upsert_evm_properties!
INSERT INTO evm_properties (address_id, native_balance, is_eoa, is_safe)
VALUES (:address_id, :native_balance, :is_eoa, :is_safe)
ON CONFLICT(address_id) DO UPDATE SET
    native_balance = COALESCE(excluded.native_balance, native_balance),
    is_eoa = COALESCE(excluded.is_eoa, is_eoa),
    is_safe = COALESCE(excluded.is_safe, is_safe);

-- name: upsert_safe_wallet!
INSERT INTO safe_wallets (address_id, threshold, nonce, owner_count)
VALUES (:address_id, :threshold, :nonce, :owner_count)
ON CONFLICT(address_id) DO UPDATE SET
    threshold = COALESCE(excluded.threshold, threshold),
    nonce = COALESCE(excluded.nonce, nonce),
    owner_count = COALESCE(excluded.owner_count, owner_count);

-- name: insert_safe_wallet_owner!
INSERT INTO safe_wallet_owners (safe_address_id, owner_address)
VALUES (:safe_address_id, :owner_address)
ON CONFLICT(safe_address_id, owner_address) DO NOTHING;
