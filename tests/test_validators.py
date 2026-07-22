from natk.utils.validators import validate_ip, validate_cidr, validate_port, validate_hostname, validate_mac, sanitize_filename
class TestValidators:
    def test_valid_ip(self):
        assert validate_ip('192.168.1.1') == True
        assert validate_ip('10.0.0.1') == True
    def test_invalid_ip(self):
        assert validate_ip('999.999.999.999') == False
        assert validate_ip('not-an-ip') == False
    def test_valid_cidr(self):
        assert validate_cidr('10.0.0.0/24') == True
    def test_invalid_cidr(self):
        assert validate_cidr('not-cidr') == False
    def test_valid_port(self):
        assert validate_port(80) == True
        assert validate_port(65535) == True
    def test_invalid_port(self):
        assert validate_port(0) == False
        assert validate_port(70000) == False
        assert validate_port(-1) == False
    def test_valid_hostname(self):
        assert validate_hostname('server01') == True
        assert validate_hostname('router.example.com') == True
    def test_invalid_hostname(self):
        assert validate_hostname('') == False
    def test_valid_mac(self):
        assert validate_mac('AA:BB:CC:DD:EE:FF') == True
        assert validate_mac('aa-bb-cc-dd-ee-ff') == True
    def test_invalid_mac(self):
        assert validate_mac('invalid') == False
    def test_sanitize(self):
        assert sanitize_filename('test/../file') == 'test__file'
        assert ' ' not in sanitize_filename('bad name')
