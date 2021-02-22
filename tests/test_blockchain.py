import blockchain

def test_Signature():
    sk = blockchain.SK()
    signature = sk.sign(b"This is a test.")
    assert signature.verify(b"This is a test.")
    assert not signature.verify(b"This is a test")
    
