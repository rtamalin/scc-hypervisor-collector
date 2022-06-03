import mock
import pytest

from tests import utils

class TestSCCHypervisorCollectorCLI:
    """Class for scc-hypervisor-collector cli tests"""
    def test_no_arguments(self, capsys, monkeypatch, scc_hypervisor_collector_cli):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()

    def test_bad_option(self, capsys, monkeypatch, scc_hypervisor_collector_cli):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--bad"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()

        out, err = capsys.readouterr()
        assert "scc-hypervisor-collector: error: unrecognized arguments: --bad\n" in err

    def test_version_option(self, capsys, monkeypatch, scc_hypervisor_collector_cli):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--version"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        out, err = capsys.readouterr()
        assert scc_hypervisor_collector_cli.cli_version in out

    def test_help_option(self, capsys, monkeypatch, scc_hypervisor_collector_cli):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--help"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        out, err = capsys.readouterr()
        assert "usage: scc-hypervisor-collector " in out

    def test_check_option_success(self, capsys, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--check", "--config", "tests/unit/data/config/default/default.yaml"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        for record in caplog.records:
            assert record.levelname != 'DEBUG' #default log level is INFO

    def test_check_option_failure(self, capsys, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--check", "--config-dir", "tests/unit/data/config/invalid"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        for record in caplog.records:
            assert record.levelname != 'DEBUG' #default log level is INFO

    def test_quiet_option(self, capsys, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--quiet", "--config", "tests/unit/data/config/default/default.yaml"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        for record in caplog.records:
            assert record.levelname != 'DEBUG'
        assert caplog.records[-1].levelname == 'ERROR' and 'query failed after 3 attempts' in caplog.text

    def test_verbose_option(self, capsys, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--verbose", "--config", "tests/unit/data/config/default/default.yaml"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        assert caplog.records[0].levelname == 'DEBUG'
        assert caplog.records[-1].levelname == 'ERROR' and 'query failed after 3 attempts' in caplog.text

    def test_verbose_sensitive_field(self, capsys, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector", "--verbose", "--config", "tests/unit/data/config/mock/config.yaml"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        assert "3tjdla3gEP4WqkPd" not in caplog.text

    def test_sensitive_field(self, capsys, monkeypatch, scc_hypervisor_collector_cli, caplog):
        monkeypatch.setattr("sys.argv", ["scc-hypervisor-collector","--config", "tests/unit/data/config/mock/config.yaml"])
        with pytest.raises(SystemExit):
            scc_hypervisor_collector_cli.main()
        assert "3tjdla3gEP4WqkPd" not in caplog.text