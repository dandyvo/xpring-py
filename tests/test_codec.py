import pytest

import xpring.codecs as codecs
from xpring.ciphers import ed25519, secp256k1

codec = codecs.DEFAULT_CODEC

ED25519_EXAMPLES = [
    ('4C3A1D213FBDFB14C7C28D609469B341', 'sEdTM1uX8pu2do5XvTnutH6HsouMaM2'),
    ('00000000000000000000000000000000', 'sEdSJHS4oiAdz7w2X2ni1gFiqtbJHqE'),
    ('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF', 'sEdV19BLfeQeKdEXyYA4NhjPJe6XBfG')
]

SECP256K1_EXAMPLES = [
    ('CF2DE378FBDD7E2EE87D486DFB5A7BFF', 'sn259rEFXrQrWyx3Q7XneWcwV6dfL'),
    ('00000000000000000000000000000000', 'sp6JS7f14BuwFY8Mw6bTtLKWauoUs'),
    ('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF', 'saGwBRReqUNKuWNLpUAq8i8NkXEPN')
]


@pytest.mark.parametrize('hex,encoded', ED25519_EXAMPLES)
def test_encode_ed25519_seed(hex, encoded):
    assert codec.encode_seed(bytes.fromhex(hex), ed25519) == encoded


@pytest.mark.parametrize('hex,encoded', ED25519_EXAMPLES)
def test_decode_ed25519_seed(hex, encoded):
    bites, cipher = codec.decode_seed(encoded)
    assert cipher == ed25519
    assert bites.hex().upper() == hex


@pytest.mark.parametrize('hex,encoded', SECP256K1_EXAMPLES)
def test_encode_secp256k1_seed(hex, encoded):
    assert codec.encode_seed(bytes.fromhex(hex), secp256k1) == encoded


@pytest.mark.parametrize('hex,encoded', SECP256K1_EXAMPLES)
def test_decode_secp256k1_seed(hex, encoded):
    bites, cipher = codec.decode_seed(encoded)
    assert cipher == secp256k1
    assert bites.hex().upper() == hex