import blockchain


def test_Signature():
    sk1 = blockchain.SK()
    sk2 = blockchain.SK()
    signature = blockchain.Signature.from_raw(sk1.sign(b"This is a test.").raw)
    wrong_sig = blockchain.Signature(signature.signature, sk2.vk)
    assert signature.verify(b"This is a test.")
    assert not signature.verify(b"This is a test")
    assert not wrong_sig.verify(b"This is a test.")
    assert not wrong_sig.verify(b"This is a test")
