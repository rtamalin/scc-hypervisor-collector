import pytest
import json
import mock

from scc_hypervisor_collector.api import ConfigManager, CollectionScheduler, HypervisorCollector
from scc_hypervisor_collector import cli


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
def scc_hypervisor_collector_cli():
    return cli

def pytest_configure(config):
    config.addinivalue_line(
        "markers", ('config: the configuration passed on to config manager')
    )


