-- name: create_addresses_table!
CREATE TABLE IF NOT EXISTS addresses (
    network TEXT,
    address TEXT,
    native_balance TEXT,
    is_eoa BOOLEAN,
    PRIMARY KEY (network, address)
);

-- name: create_safe_wallets_table!
CREATE TABLE IF NOT EXISTS safe_wallets (
    network TEXT,
    address TEXT,
    threshold INTEGER,
    nonce INTEGER,
    owner_count INTEGER,
    PRIMARY KEY (network, address),
    FOREIGN KEY (network, address) REFERENCES addresses (network, address)
);

-- name: create_safe_wallet_owners_table!
CREATE TABLE IF NOT EXISTS safe_wallet_owners (
    network TEXT,
    safe_address TEXT,
    owner_address TEXT,
    PRIMARY KEY (network, safe_address, owner_address),
    FOREIGN KEY (network, safe_address)
    REFERENCES safe_wallets (network, address)
);

-- name: insert_into_addresses!
INSERT INTO addresses (
    network,
    address
) VALUES (
    :network,
    :address
) ON CONFLICT(network, address)
DO NOTHING;

-- name: insert_into_safe_wallets!
INSERT INTO safe_wallets (
    network,
    address
) VALUES (
    :network,
    :address
) ON CONFLICT(network, address)
DO NOTHING;

-- name: insert_into_safe_wallet_owners!
INSERT INTO safe_wallet_owners (
    network,
    safe_address,
    owner_address
) VALUES (
    :network,
    :safe_address,
    :owner_address
) ON CONFLICT(network, safe_address, owner_address)
DO NOTHING;

-- name: update_native_balance!
UPDATE addresses
SET native_balance = :value
WHERE network = :network AND address = :address;

-- name: update_is_eoa!
UPDATE addresses
SET is_eoa = :value
WHERE network = :network AND address = :address;

-- name: update_safe_threshold!
UPDATE safe_wallets
SET threshold = :value
WHERE network = :network AND address = :address;

-- name: update_safe_nonce!
UPDATE safe_wallets
SET nonce = :value
WHERE network = :network AND address = :address;

-- name: update_safe_owner_count!
UPDATE safe_wallets
SET owner_count = :value
WHERE network = :network AND address = :address;
