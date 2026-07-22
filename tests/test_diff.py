from natk.core.diff import ConfigDiffer
class TestConfigDiffer:
    def test_compare_no_files(self):
        d = ConfigDiffer()
        result = d.compare('host', 'rev1', 'rev2')
        assert len(result) > 0
    def test_summary_no_files(self):
        d = ConfigDiffer()
        s = d.summary('host', 'rev1', 'rev2')
        assert s['total'] >= 0
    def test_has_changes_no_files(self):
        d = ConfigDiffer()
        assert d.has_changes('host', 'rev1', 'rev2') == True
