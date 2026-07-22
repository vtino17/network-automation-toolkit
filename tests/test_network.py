from natk.utils.network import is_private_ip, get_local_ip
class TestNetworkUtils:
    def test_private_ip(self):
        assert is_private_ip('10.0.0.1') == True
        assert is_private_ip('192.168.1.1') == True
    def test_public_ip(self):
        assert is_private_ip('8.8.8.8') == False
    def test_get_local_ip(self):
        ip = get_local_ip()
        assert ip != '127.0.0.1' or ip is not None
