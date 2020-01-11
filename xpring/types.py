import typing as t

# 16 bytes.
Seed = t.NewType('Seed', bytes)
# Base58 encoding (with prefix and checksum) of
# a seed and a choice of signing algorithm.
EncodedSeed = t.NewType('EncodedSeed', str)

# 32 bytes.
PrivateKey = t.NewType('PrivateKey', bytes)

# 33 bytes.
PublicKey = t.NewType('PublicKey', bytes)
# 20 bytes computed from a public key.
AccountId = t.NewType('AccountId', bytes)
# Base58 encoding (with prefix and checksum) of an account ID.
# https://xrpl.org/accounts.html#address-encoding
Address = t.NewType('Address', str)

Signature = t.NewType('Signature', bytes)