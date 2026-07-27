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
    def test_sanitize_strips_traversal_sequences(self):
        assert '..' not in sanitize_filename('../../etc/passwd')
        assert '..' not in sanitize_filename('....//x')
        assert '..' not in sanitize_filename('a/../../b')
    def test_sanitize_never_returns_a_directory_reference(self):
        for hostile in ('..', '.', '', '_', '...', './.'):
            assert sanitize_filename(hostile) == 'unnamed'
    def test_sanitize_result_stays_inside_the_target_directory(self):
        import os
        base = '/var/backups'
        for hostile in ('..', '../..', '../../etc/passwd', 'test/../file', ''):
            joined = os.path.normpath(os.path.join(base, sanitize_filename(hostile)))
            assert joined.startswith(base + os.sep)
    def test_sanitize_leaves_ordinary_names_alone(self):
        assert sanitize_filename('router01-config.txt') == 'router01-config.txt'
        assert sanitize_filename('backup.2026-07-27.json') == 'backup.2026-07-27.json'
    def test_sanitize_fallback_is_configurable(self):
        assert sanitize_filename('..', fallback='device') == 'device'
