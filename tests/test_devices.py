class TestBaseDevice:
    def test_device_creation(self):
        from natk.devices.base import BaseDevice
        class TestDev(BaseDevice):
            def connect(self): pass
            def disconnect(self): pass
            def get_config(self): return ''
            def get_facts(self): return {}
            def execute(self, cmd): return ''
        d = TestDev('test', '10.0.0.1')
        assert d.hostname == 'test'
        assert d.ip == '10.0.0.1'
    def test_device_repr(self):
        from natk.devices.base import BaseDevice
        class TestDev(BaseDevice):
            def connect(self): pass
            def disconnect(self): pass
            def get_config(self): return ''
            def get_facts(self): return {}
            def execute(self, cmd): return ''
        d = TestDev('r1', '10.0.0.1')
        r = repr(d)
        assert 'TestDev' in r
    def test_device_ping(self):
        from natk.devices.base import BaseDevice
        class TestDev(BaseDevice):
            def connect(self): pass
            def disconnect(self): pass
            def get_config(self): return ''
            def get_facts(self): return {}
            def execute(self, cmd): return ''
        d = TestDev('localhost', '127.0.0.1')
        assert d.ping(count=1) == True
