/*
    TODO
    The fields safe_owner_count and `safe_threshold`
    are denormalized for perfomance.
    Will refactor to a separate 'safes' table if scaling requires.
*/

-- name: create_addresses_table!
CREATE TABLE IF NOT EXISTS addresses (
    network TEXT,
    address TEXT,
    native_balance TEXT,
    is_eoa BOOLEAN,
    is_safe BOOLEAN,
    safe_owner_count INTEGER,
    safe_threshold INTEGER,
    safe_nonce INTEGER,
    PRIMARY KEY (network, address)
)

-- name: create_safe_owners_table!
CREATE TABLE IF NOT EXISTS safe_owners (
    network TEXT,
    safe_address TEXT,
    owner_address TEXT,
    PRIMARY KEY (network, safe_address, owner_address),
    FOREIGN KEY (network, safe_address)
    REFERENCES addresses (network, address)
)

-- name: insert_into_addresses!
INSERT INTO addresses (
    network,
    address
) VALUES (
    :network,
    :address
) ON CONFLICT(network, address)
DO NOTHING;

-- name: insert_into_safe_owners!
INSERT INTO safe_owners (
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

-- name: update_is_safe!
UPDATE addresses
SET is_safe = :value
WHERE network = :network AND address = :address;

-- name: update_safe_threshold!
UPDATE addresses
SET safe_threshold = :value
WHERE network = :network AND address = :address;

-- name: update_safe_nonce!
UPDATE addresses
SET safe_nonce = :value
WHERE network = :network AND address = :address;

-- name: update_safe_owner_count!
UPDATE addresses
SET safe_owner_count = :value
WHERE network = :network AND address = :address;
