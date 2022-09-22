import pathlib
import pytest
import os

from scc_hypervisor_collector.api import (
    ConfigManager,
    CollectionResults,
    HypervisorCollector,
)
from scc_hypervisor_collector import cli


@pytest.fixture(scope="session", autouse=True)
def data_config_permissions(pytestconfig):
    config = pytestconfig
    # Get repo root directory, supporting older versions of pytest
    # that don't have rootpath
    if hasattr(config, 'rootpath'):
        reporoot = config.rootpath
    else:
        reporoot = pathlib.Path(config.rootdir)
    location = reporoot / "tests/unit/data"
    # Update file permissions of the tests/unit/data folder
    for root, dirs, files in os.walk(location):
        for dir in [os.path.join(root, d) for d in dirs]:
            os.chmod(dir, 0o700)
        for file in [os.path.join(root, f) for f in files]:
            os.chmod(file, 0o600)

@pytest.fixture
def config_manager(request):
    marker = request.node.get_closest_marker("config")
    return ConfigManager(config_file=marker.args[0], config_dir=marker.args[1])

@pytest.fixture
def backendid(request):
    if getattr(request, 'param', None):
        return request.param

@pytest.fixture
def hypervisor_collector(backendid, config_manager):
    config_data = config_manager.config_data
    filtered_list = [b for b in config_data.backends if b.id == backendid]
    hypervisor_coll = HypervisorCollector(backend=filtered_list[0])
    return hypervisor_coll

@pytest.fixture
def scc_hypervisor_collector_cli(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    return cli

@pytest.fixture
def collected_results(request):
    marker = request.node.get_closest_marker("config")
    colresults = CollectionResults()
    colresults.load(pathlib.Path(marker.args[0]))
    return colresults

def pytest_configure(config):
    config.addinivalue_line(
        "markers", ('config: the configuration passed on to config manager')
    )
