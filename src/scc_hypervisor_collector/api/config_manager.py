"""
SCC Hypervisor Collector ConfigManager.

The ConfigManager can be used to load the specified configuration
data and validate that it contains the settings required for correct
operation of the SCC Hypervisor Collector.
"""

import getpass
import logging
import stat
from pathlib import Path
from typing import (Any, Dict, List, Optional)
import yaml

from .configuration import CollectorConfig
from .exceptions import (
    ConfigManagerError,
    ConflictingBackendsError,
    EmptyConfigurationError,
    NoConfigFilesFoundError,
)

LOG = logging.getLogger()


class ConfigManager:
    """Configuration Management for the scc-hypervisor-collector.

    The ConfigManager takes the following arguments:
      * config_file (str): optional path to a YAML config file.
      * config_dir (str): optional path to a directory containing
            YAML config files

    If a config directory is specified then any YAML files, i.e.
    those with a '.yaml' or '.yml' extension, found directly under
    it will be added (in lexcial sort order) to the list of config
    files to be processed.

    If a config file is specified then it will be added to the end
    of the list of files to be processed, ensuring that the settings
    in it will supercede those that may have been previously loaded.

    When loading the configuration settings the list of config files
    is processed in order, with each file's content being merged over
    the existing content, until all files are processed.
    """

    def __init__(self, config_file: Optional[str] = None,
                 config_dir: Optional[str] = None,
                 check: bool = False):
        """Initialiser for ConfigManager"""

        LOG.debug("config_file: %s, config_dir: %s", repr(config_file),
                  repr(config_dir))

        if not config_file and not config_dir:
            raise ConfigManagerError("At least one of config_file and "
                                     "config_dir must be specified!")

        # Save parameters, converting to Path objects if specified.
        self._config_file: Optional[Path] = (
            Path(config_file) if config_file else None
        )
        self._config_dir: Optional[Path] = (
            # use expanduser() to expand ~'s
            Path(config_dir).expanduser() if config_dir else None
        )

        self._check = check

        # Lazy loaded configuration data
        self._config_data: Optional[CollectorConfig] = None

        # List of potential config sources
        self._config_files: List[Path] = []

    def _list_config_files(self) -> List:
        """Generate list of possible config files to be loaded, in the order
        that they should be loaded.

        Returns:
            List: The (possibly empty) ordered list of config files to load.
        """
        cfg_files: List[Path] = []

        # Handle config directory first
        if self._config_dir:
            if self._config_dir.exists():
                self.check_permission(self._config_dir)
            # Find both *.yml and *.yaml files
            cfg_files.extend(self._config_dir.glob("*.yml"))
            cfg_files.extend(self._config_dir.glob("*.yaml"))

            # Lexically sort found files
            cfg_files.sort()

        LOG.debug("Lexically sorted config directory files list: %s",
                  repr(cfg_files))

        # If a config file was specified then append it to the sorted
        # list of found files ensuring it's contents will supercede
        # previous config settings
        if self._config_file:
            if self._config_file.exists():
                cfg_files.append(self._config_file)

        if not cfg_files:
            raise NoConfigFilesFoundError("No config files found!",
                                          # pass path strings as extra args
                                          str(self._config_file),
                                          str(self._config_dir))

        LOG.debug("Config Files found: %s",
                  repr([str(f) for f in cfg_files]))

        for file in cfg_files:
            self.check_permission(file)

        return cfg_files

    @staticmethod
    def check_permission(path: Path) -> None:
        """Check if path has the required permissions """
        current_user = getpass.getuser()
        stats = path.stat()
        mode = stats.st_mode
        if path.owner() != current_user:
            msg = f"{path} not owned by the user {current_user}"
            raise ConfigManagerError(msg)
        if path.is_dir():
            if stat.S_IMODE(mode) != 0o700:
                msg = f"User { current_user } should have full access to " \
                      f"{path} but group and others should have no access."
                raise ConfigManagerError(msg)
        if path.is_file():
            if stat.S_IMODE(mode) != 0o600:
                msg = f"User {current_user} should have read/write access " \
                      f"to {path} but group and others should have no access."
                raise ConfigManagerError(msg)

    @staticmethod
    def _remove_idless_duplicates(backend: Dict[str, Any],
                                  backends: List[Dict[str, Any]]) -> None:
        """Remove any id-less matches for backend from backends list."""

        no_id_backend = backend.copy()
        existing_id = no_id_backend.pop('id')
        if no_id_backend in backends:
            LOG.debug('Dropping duplicated id-less backend for matching '
                      'backend with id %s', repr(existing_id))
            backends.remove(no_id_backend)

    @staticmethod
    def _get_backends(cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
        """ Return the list of backends - an empty list if
        backends section is empty
        """
        backends: List[Dict[str, Any]] = cfg.get('backends', [])
        if backends is None:
            backends = []
        return backends.copy()

    def _merge_config_data(self, old_cfg: Dict[str, Any],
                           new_cfg: Dict[str, Any]) -> None:
        """Merge the new_cfg into the old_cfg.

        Handle merging backend lists appropriately; duplicates
        should be dropped, and conflicting entries should fail.
        """
        backends_in_old: bool = 'backends' in old_cfg
        backends_in_new: bool = 'backends' in new_cfg

        # Make lightweight copies of backends lists in old and new cfgs
        old_backends: List[Dict[str, Any]] = self._get_backends(old_cfg)
        new_backends: List[Dict[str, Any]] = self._get_backends(new_cfg)

        # Merge new config settings over existing config settings
        old_cfg.update(new_cfg)

        # Unless both configs had a backends entry the result of the
        # update() is the desired result.
        if not all((backends_in_old, backends_in_new)):
            return

        # Check for exact duplicates and remove any found
        duplicates = [b for b in new_backends if b in old_backends]
        if duplicates:
            LOG.debug(
                "Found %d duplicates: %s", len(duplicates),
                repr([{'id': b.get('id', 'NO_ID_SPECIFIED'),
                       'module': b.get('module', 'NO_MODULE_SPECIFIED')}
                      for b in duplicates])
            )
            new_backends = [b for b in new_backends if b not in old_backends]

        # Check for duplicated id-less backends entries, i.e. if there
        # any entries in either list without an id that match an entry
        # in the other list with an id. If so retain the one with an id.
        for backend in old_backends:
            if 'id' in backend:
                self._remove_idless_duplicates(backend, new_backends)

        for backend in new_backends:
            if 'id' in backend:
                self._remove_idless_duplicates(backend, old_backends)

        # Check for conflicts and fail if any found
        old_ids = [b['id'] for b in old_backends if 'id' in b]
        conflicts = [b for b in new_backends if b['id'] in old_ids]
        if conflicts:
            LOG.debug("Found %d conflicts for these backend ids %s",
                      len(conflicts), repr(old_ids))
            raise ConflictingBackendsError("Conflicting Backend IDs",
                                           old_ids)

        # Combined lists should now contain unique entries.
        old_cfg['backends'] = old_backends + new_backends

    def _load_config(self) -> Dict:
        """Load the specified config files, if any, merging content
        together.
        Returns:
            Dict: The (possibly empty) dictionary of config data.
        """

        cfg_data: Dict[str, Any] = {}
        for cfg_file in self.config_files:
            file_data = yaml.safe_load(cfg_file.read_text(encoding="utf-8"))

            if file_data is None:
                LOG.debug("Empty config file: %s", repr(str(cfg_file)))
                continue

            # Merge new data over existing data, combining any new backends
            # with existing backends, eliminating duplicates as needed.
            self._merge_config_data(cfg_data, file_data)

        if not cfg_data:
            raise EmptyConfigurationError("No config settings loaded!")

        LOG.debug("Config Files processed: %s", repr(self.config_files))
        return cfg_data

    @property
    def config_files(self) -> List[Path]:
        """Return the list of identified config files."""
        if not self._config_files:
            self._config_files = self._list_config_files()
        return self._config_files

    @property
    def config_file(self) -> Optional[Path]:
        """Return the config_file argument specified when class was
           instantiated."""
        return self._config_file

    @property
    def config_dir(self) -> Optional[Path]:
        """Return the config_dir argument specified when class was
           instantiated."""
        return self._config_dir

    @property
    def config_data(self) -> CollectorConfig:
        """Return the config_data loaded from the specifed config
           sources."""
        if self._config_data is None:
            self._config_data = CollectorConfig(self._load_config(),
                                                _check=self._check)
        return self._config_data
