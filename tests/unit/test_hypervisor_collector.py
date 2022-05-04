import mock
import pytest


from scc_hypervisor_collector.api import exceptions, HypervisorCollector
from tests import utils


class TestHypervisorCollector:

    @pytest.mark.config('tests/unit/data/config/mock/config.yaml', None)
    @pytest.mark.parametrize('backendid', ['vcenter1', 'libvirt1'], indirect=True)
    def test_hypervisor_collector_results(self, hypervisor_collector, backendid):
        hypervisor_collector = hypervisor_collector
        mfilename = 'tests/unit/data/config/mock/mock_' + backendid + '.json'
        with mock.patch('scc_hypervisor_collector.api.HypervisorCollector.results', utils.read_mock_data(mfilename)):
            utils.validate_mock_data(hypervisor_collector, backendid)

    @pytest.mark.config('tests/unit/data/config/mock/config.yaml', None)
    @pytest.mark.parametrize('backendid', ['vcenter1', 'libvirt1'], indirect=True)
    def test_hypervisor_collector_query_backend(self, hypervisor_collector, backendid):
        hypervisor_collector = hypervisor_collector
        mfilename = 'tests/unit/data/config/mock/mock_' + backendid + '.json'
        with mock.patch('scc_hypervisor_collector.api.HypervisorCollector._query_backend',
                        return_value=utils.read_mock_data(mfilename)):
            utils.validate_mock_data(hypervisor_collector, backendid)

    @pytest.mark.config('tests/unit/data/config/mock/config.yaml', None)
    @pytest.mark.parametrize('backendid', ['vcenter1', 'libvirt1'], indirect=True)
    def test_hypervisor_collector_default_retries(self, hypervisor_collector, backendid):
        mfilename = 'tests/unit/data/config/mock/mock_' + backendid + '.json'
        with mock.patch('scc_hypervisor_collector.api.HypervisorCollector._worker_run',
                        side_effect=[None, None, utils.read_mock_data(mfilename)]): #3rd retry success
            utils.validate_mock_data(hypervisor_collector, backendid)

    @pytest.mark.config('tests/unit/data/config/mock/config.yaml', None)
    @pytest.mark.parametrize('backendid', ['vcenter1', 'libvirt1'], indirect=True)
    @pytest.mark.parametrize('retries', [2], indirect=True)
    def test_hypervisor_collector_two_retries_success(self, hypervisor_collector_with_retries, retries, backendid):
        mfilename = 'tests/unit/data/config/mock/mock_' + backendid + '.json'
        with mock.patch('scc_hypervisor_collector.api.HypervisorCollector._worker_run',
                        side_effect=[None, utils.read_mock_data(mfilename)]): #2nd retry success
            assert retries == hypervisor_collector_with_retries.retries
            utils.validate_mock_data(hypervisor_collector_with_retries, backendid)

    @pytest.mark.config('tests/unit/data/config/mock/config.yaml', None)
    @pytest.mark.parametrize('backendid', ['vcenter1', 'libvirt1'], indirect=True)
    @pytest.mark.parametrize('retries', [4], indirect=True)
    def test_hypervisor_collector_exhausted_retries(self, hypervisor_collector_with_retries, retries, backendid):
        with mock.patch('scc_hypervisor_collector.api.HypervisorCollector._worker_run',
                        side_effect=[None, None, None, None]): #4 retries failure
            with pytest.raises(exceptions.HypervisorCollectorRetriesExhausted) as excinfo:
                hypervisor_collector_with_retries.results
            assert 'Backend' in str(excinfo.value)
            assert 'module' in str(excinfo.value)
            assert 'retries' in str(excinfo.value)


@pytest.fixture
def retries(request):
    return request.param

@pytest.fixture
def hypervisor_collector_with_retries(backendid, retries, config_manager):
    config_data = config_manager.config_data
    filtered_list = [b for b in config_data.backends if b.id == backendid]
    hypervisor_coll = HypervisorCollector(backend=filtered_list[0], retries=retries)
    return hypervisor_coll
