import os
import pytest

from scc_hypervisor_collector.api import exceptions, ConfigManager, CredentialsConfig, BackendConfig

class TestConfigManager:

    @pytest.mark.config('tests/unit/data/config/default/default.yaml', None)
    def test_single_file_config_load(self, config_manager):
        config_data = config_manager._load_config()
        assert config_manager.config_file._str == 'tests/unit/data/config/default/default.yaml'
        assert not config_manager.config_dir
        assert config_data.get('credentials')['scc']['username'] == 'default_scc_username'
        assert config_data.get('credentials')['scc']['password'] == 'default_scc_password'

    @pytest.mark.config(None, 'tests/unit/data/config/empty')
    def test_empty_config_load(self, config_manager):
        with pytest.raises(exceptions.EmptyConfigurationError) as excinfo:
            config_manager._load_config()
        assert 'No config settings loaded!' in str(excinfo.value)

    @pytest.mark.config(None, 'tests/unit/data/config/nonexisting')
    def test_nonexisting_dir_config_load(self, config_manager):
        with pytest.raises(exceptions.NoConfigFilesFoundError) as excinfo:
            config_manager._load_config()
        assert 'No config files found' in str(excinfo.value)

    @pytest.mark.config('tests/unit/data/config/nonexisting.yml', None)
    def test_nonexisting_file_config_load(self, config_manager):
        with pytest.raises(exceptions.NoConfigFilesFoundError) as excinfo:
            config_manager._load_config()
        assert 'No config files found' in str(excinfo.value)

    @pytest.mark.config(None, 'tests/unit/data/config/conflicts')
    def test_backend_conflicts_config_load(self, config_manager):
        with pytest.raises(exceptions.ConflictingBackendsError) as excinfo:
            config_manager._load_config()
        assert 'Conflicting Backend IDs' in str(excinfo.value)
        assert 'multiple_VCenter_1' in excinfo.value.backend_ids

    @pytest.mark.config(None, 'tests/unit/data/config/invalid')
    def test_invalid_dir_config_load(self, config_manager):
        config_data = config_manager._load_config()
        # validation is not performed in the _load_config() call and
        # hence the yaml file is successfully read
        assert len(config_data) > 0

    @pytest.mark.config(None, 'tests/unit/data/config/lexorder')
    def test_lexorder_config_load(self, config_manager):
        config_data = config_manager._load_config()
        # merges all contents of all the files found in the directory together.
        # if the same credentials section is defined in multiple files,
        # it keeps only the section that was last read based
        # on the lexorder
        assert config_data.get('credentials')['scc']['username'] == 'second_scc_username'
        assert config_data.get('credentials')['scc']['username'] != 'first_scc_username'

        # for backends
        backends = config_data.get('backends')
        backend_config_ids = []
        for backend in backends:
            backend_config_ids.append(backend['id'])
        assert "first_vmware_1" in backend_config_ids
        assert "second_vmware_1" in backend_config_ids

    @pytest.mark.config(None, 'tests/unit/data/config/multiple')
    def test_dir_config_load(self, config_manager):
        config_data = config_manager._load_config()
        assert config_data.get('credentials')['scc']['username'] == 'm_scc_username'
        assert config_data.get('credentials')['scc']['username'] != 'm_scc_password'

        # for backends
        backends = config_data.get('backends')
        backend_config_ids = []
        for backend in backends:
            backend_config_ids.append(backend['id'])
        assert "multiple_Libvirt_1" in backend_config_ids
        assert "multiple_VCenter_1" in backend_config_ids

    @pytest.mark.config('tests/unit/data/config/multiple/scc.yml', 'tests/unit/data/config/multiple')
    def test_specify_config_file_and_dir_load(self, config_manager):
        config_data = config_manager._load_config()
        assert len(config_data.get('credentials')) == 1

    @pytest.mark.config('tests/unit/data/config/default/default.yaml', None)
    def test_single_file_config_data(self, config_manager):
        config_data = config_manager.config_data
        backend_config = config_data.backends
        credentials_config = config_data.credentials
        scc_config = credentials_config.scc
        # validate default.yaml has properties - credentials + backends
        assert len(backend_config) == 2
        assert len(credentials_config) == 1
        assert len(scc_config) == 2
        assert scc_config.username == 'default_scc_username'
        assert scc_config.password == 'default_scc_password'

    @pytest.mark.config('tests/unit/data/config/invalid/invalid.yaml', None)
    def test_invalid_config_data(self, config_manager):
        with pytest.raises(exceptions.CollectorConfigContentError):
            assert "Invalid configuration data provided" in config_manager.config_data

    @pytest.mark.config(None, 'tests/unit/data/config/multiple')
    def test_dir_config_data(self, config_manager):
        config_data = config_manager.config_data
        backend_config = config_data.backends
        credentials_config = config_data.credentials
        scc_config = credentials_config.scc
        #assert both libvirt and vmware backends
        assert len(backend_config) == 2
        assert len(credentials_config) == 1
        assert len(scc_config) == 2

    @pytest.mark.config('tests/unit/data/config/default/default.yaml', None)
    def test_backend_module(self, config_manager):
        config_data = config_manager.config_data
        backend_config = config_data.backends
        assert len(backend_config) == 2
        for backend in backend_config:
            assert backend.module

    @pytest.mark.config('tests/unit/data/config/default/default.yaml', None)
    def test_password_sensitivity(self, config_manager):
        config_data = config_manager.config_data
        credentials_config = config_data.credentials
        scc_config = credentials_config.scc
        assert 'password' in scc_config.sensitive_fields
        scc_sanitized_config = scc_config._sanitized_config()
        assert '*****' in scc_sanitized_config['password']
        assert '*****' in scc_sanitized_config['password']
        assert '*****' in str(scc_config)

    @pytest.mark.config('tests/unit/data/config/default/default.yaml', None)
    def test_assign_sensitivity_scc_username_neg(self, config_manager):
        config_data = config_manager.config_data
        credentials_config = config_data.credentials
        scc_config = credentials_config.scc
        assert 'password' in scc_config.sensitive_fields
        assert '***' in repr(scc_config._sanitized_config()['password'])
        assert '***' in str(scc_config._sanitized_config()['password'])
        new_set_sensitive_fields = {'username', 'password'}
        # You should not be able to update these properties
        with pytest.raises(AttributeError):
            scc_config.sensitive_fields = new_set_sensitive_fields

    @pytest.mark.config('tests/unit/data/config/negative/emptybackends.yaml', None)
    def test_empty_backends_section(self, config_manager):
        with pytest.raises(exceptions.BackendConfigError):
            config_manager.config_data

    @pytest.mark.config('tests/unit/data/config/negative/idlessbackend.yaml', None)
    def test_missing_backendid(self, config_manager):
        with pytest.raises(exceptions.BackendConfigError):
            config_manager.config_data

    @pytest.mark.config('tests/unit/data/config/default/default.yaml', None)
    def test_missing_fields(self, config_manager):
        config_data = config_manager.config_data
        assert len(config_data.missing_fields) == 0

    @pytest.mark.config('tests/unit/data/config/negative/nomodulebackend.yaml', None)
    def test_error_with_nomodule(self, config_manager):
        with pytest.raises(exceptions.BackendConfigError):
            config_manager.config_data

    @pytest.mark.config('tests/unit/data/config/negative/unsupportedbackend.yaml', None)
    def test_error_with_unsupportedmodule(self, config_manager):
        with pytest.raises(exceptions.BackendConfigError):
            config_manager.config_data

    @pytest.mark.config('tests/unit/data/config/default/default.yaml', None)
    def test_backend_config_gatherer(self, config_manager):
        config_data = config_manager.config_data
        backends = config_data.get('backends')
        for backend in backends:
            assert backend.gatherer

    @pytest.mark.config('tests/unit/data/config/default/default.yaml', None)
    def test_backend_config_id(self, config_manager):
        config_data = config_manager.config_data
        backends = config_data.get('backends')
        for backend in backends:
            assert backend.id

    @pytest.mark.config('tests/unit/data/config/default/default.yaml', None)
    def test_backend_config_worker(self, config_manager):
        config_data = config_manager.config_data
        backends = config_data.get('backends')
        for backend in backends:
            assert backend.worker

    @pytest.mark.config('tests/unit/data/config/default/default.yaml', None)
    def test_backend_config_worker_params(self, config_manager):
        config_data = config_manager.config_data
        backends = config_data.get('backends')
        for backend in backends:
            assert backend.worker_params

    @pytest.mark.config('tests/unit/data/config/default/default.yaml', None)
    def test_config_key_deletion(self, config_manager):
        config_data = config_manager.config_data
        config_data.__delitem__('credentials')
        assert 'credentials' not in config_data

    def test_no_config_file_nor_dir(self):
        with pytest.raises(exceptions.ConfigManagerError, match=r"At least one of .* must be specified!"):
            ConfigManager(config_file=None, config_dir=None)

    def test_config_file_incorrect_permissions(self):
        filename='tests/unit/data/config/perm/perm.yml'
        os.chmod(filename, 0o777)
        with pytest.raises(exceptions.ConfigManagerError,
                           match=r".* should have read/write access .* but group and others should have no access."):
            config_manager = ConfigManager(config_file=filename)
            config_manager.config_data

    def test_config_dir_incorrect_permissions(self):
        dirname='tests/unit/data/config/perm'
        os.chmod(dirname, 0o777)
        with pytest.raises(exceptions.ConfigManagerError,
                           match=r".* should have full access to .* but group and others should have no access."):
            config_manager = ConfigManager(config_dir=dirname)
            config_manager.config_data

    @pytest.mark.config('tests/unit/data/config/default/default.yaml', None)
    def test_children(self, config_manager):
        children = config_manager.config_data.children
        assert len(children) == 3 # 1 scc config + 2 backend config
        for each in children:
            if isinstance(each, CredentialsConfig):
                assert each.scc.username == "default_scc_username"
                assert each.scc.password == "default_scc_password"
            if isinstance(each, BackendConfig):
                assert each.id

    @pytest.mark.config('tests/unit/data/config/default/default.yaml', None)
    def test_logger(self, config_manager):
        logger = config_manager.config_data.logger
        assert 'scc_hypervisor_collector.api.configuration' in logger.name
