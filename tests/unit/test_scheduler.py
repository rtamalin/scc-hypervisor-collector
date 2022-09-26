import mock
import getpass
import pytest

from scc_hypervisor_collector.api import (
    exceptions, CredentialsConfig, CollectorConfig,
    CollectionResults, CollectionScheduler,
    SccCredsConfig, HypervisorCollector
)
from tests import utils


class TestCollectionResults:


    @pytest.mark.config('tests/unit/data/collected/libvirt/collector.results')
    def test_collection_results_contents(self, collected_results):
        libvirt1 = collected_results.results[0]
        assert libvirt1['backend'] == 'libvirt1'
        assert libvirt1['valid'] == True
        libvirt1_details = libvirt1['details']['virtualization_hosts'][0]
        assert libvirt1_details['group_name'] == 'libvirt1'
        assert libvirt1_details['properties']['name'] == 'libvirt1.example.com'
        assert libvirt1_details['systems'][0]['properties']['vm_name'] == 'test-sle12'

    @pytest.mark.config('tests/unit/data/collected/libvirt/collector.results')
    def test_collection_results_load(self, collected_results, tmp_path):
        # create a new empty file under the dynamically generated tmp_path
        # which will be used as the input when loading collection results,
        # though we will be subsituting the results from collected_results
        # as the return value for the yaml.safe_load() operation.
        results_file = tmp_path / 'collected.results'
        results_file.touch(mode=0o600)  # ensure temp file exists with valid mode
        with mock.patch('yaml.safe_load',
                        return_value=collected_results.results) as yaml_safe_load:
            collected_results.load(results_file)
            yaml_safe_load.assert_called_once()

    @pytest.mark.config('tests/unit/data/collected/libvirt/collector.results')
    def test_collection_results_save(self, collected_results, tmp_path):
        results_file = tmp_path / 'collected.results'
        with mock.patch('yaml.safe_dump') as yaml_safe_dump:
            collected_results.save(results_file)
            yaml_safe_dump.assert_called_once()

    @pytest.mark.config('tests/unit/data/collected/libvirt/collector.results')
    def test_collection_results_load_invalid_perms(self, collected_results, tmp_path):
        # create a new empty file under the dynamically generated tmp_path
        # with invalid permissions so that it triggers the desired exception
        # that we are attempting to catch for testing purposes.
        results_file = tmp_path / 'collected.results'
        results_file.touch(mode=0o640)  # ensure temp file exists but with invalid mode
        with pytest.raises(exceptions.ResultsFilePermissionsError,
                           match=r".* should have read/write access to .* but group and others should have no access."):
            collected_results.load(results_file)

    @pytest.mark.config('tests/unit/data/collected/libvirt/collector.results')
    def test_collection_results_load_invalid_user(self, collected_results, tmp_path):
        # create a new empty file under the dynamically generated tmp_path
        # with valid permissions, but faked incorrect ownership so that it
        # triggers the desired exception that we are attempting to catch for
        # testing purposes.
        results_file = tmp_path / 'collected.results'
        results_file.touch(mode=0o600)  # ensure temp file exists with valid mode
        curr_user = getpass.getuser()
        with pytest.raises(exceptions.ResultsFilePermissionsError,
                           match=r".* not owned by the user .*"):
            with mock.patch('getpass.getuser', return_value=f"{curr_user}1"):
                collected_results.load(results_file)


class TestScheduler:


    def test_scheduler_invalid_config_none(self):
        with pytest.raises(exceptions.SchedulerInvalidConfigError):
            CollectionScheduler(config=None)

    @pytest.mark.config('tests/unit/data/config/mock/config.yaml', None)
    def test_scheduler(self, config_manager):
        backends = config_manager.config_data.backends
        hypervisor_coll_list = []
        for each in backends:
            # with mock.patch('scc_hypervisor_collector.api.HypervisorCollector.results',get_results(each.id)):
            # we are mocking the query_backend instead of the results since
            # validate_mock_data is looking at the HypervisorCollector .details and .hosts property value
            # But the .details and .hosts are based on the .results property, so accessing
            # details and hosts causes the HypervisorCollector .run() method to be called to get the results.
            mfilename = 'tests/unit/data/config/mock/mock_' + each.id + '.json'
            with mock.patch('scc_hypervisor_collector.api.HypervisorCollector._query_backend',
                            return_value=utils.read_mock_data(mfilename)):
                hypervisor_collector = HypervisorCollector(backend=each)
                utils.validate_mock_data(hypervisor_collector, each.id)
                hypervisor_coll_list.append(hypervisor_collector)
        with mock.patch('scc_hypervisor_collector.api.CollectionScheduler.hypervisors', tuple(hypervisor_coll_list)):
            scheduler = CollectionScheduler(config_manager.config_data)
            assert len(scheduler.config.backends) == 3
            assert len(scheduler.config.credentials) == 1
            assert len(scheduler.hypervisor_types) == 2
            assert len(scheduler.hypervisor_groups) == 2
            assert len(scheduler.hypervisor_groups['Libvirt']) == 2
            assert len(scheduler.hypervisor_groups['VMware']) == 1
            assert scheduler.hypervisors == tuple(hypervisor_coll_list)
            for each in scheduler.hypervisors:
                utils.validate_mock_data(each, each.backend.id)
                if each.backend.id == 'libvirt1':
                    assert 'sle15-dev' in str(each.details)
                    assert 'sle15-dev' in each.hosts
                    assert 'sle15-dev' in each.results
                if each.backend.id == 'vcenter1':
                    assert 'esx1.test.net' in str(each.details)
                    assert 'esx2.test.net' in str(each.details)
                    assert 'esx1.test.net' in each.hosts
                    assert 'esx1.test.net' in each.results
