import blockchain

def test_Signature():
    sk1 = blockchain.SK()
    sk2 = blockchain.SK()
    signature = sk1.sign(b"This is a test.")
    wrong_sig = blockchain.Signature(signature.signature, sk2.vk)
    assert signature.verify(b"This is a test.")
    assert not signature.verify(b"This is a test")
    assert not wrong_sig.verify(b"This is a test.")
    assert not wrong_sig.verify(b"This is a test")

def test_decode_Signature():
    sk = blockchain.SK()
    signature = sk.sign(b"Ceci est un test.")
    assert blockchain.decode_Signature(signature.raw).verify(b"Ceci est un test.")
    assert not blockchain.decode_Signature(signature.raw).verify(b"Ceci est un test")
