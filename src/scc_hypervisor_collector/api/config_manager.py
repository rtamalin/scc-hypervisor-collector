"""
SCC Hypervisor Collector ConfigManager.

The ConfigManager can be used to load the specified configuration
data and validate that it contains the settings required for correct
operation of the SCC Hypervisor Collector.
"""

import logging
from pathlib import Path
from typing import (Dict, List, Optional)
import yaml

from .configuration import CollectorConfig
from .exceptions import (ConfigManagerError,
                         EmptyConfigurationError,
                         NoConfigFilesFoundError)

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
                 config_dir: Optional[str] = None):
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

        return cfg_files

    def _load_config(self) -> Dict:
        """Load the specified config files, if any, merging content
        together.
        Returns:
            Dict: The (possibly empty) dictionary of config data.
        """

        cfg_data = {}
        for cfg_file in self.config_files:
            if not cfg_file.exists():
                LOG.warning("File not found: %s", repr(cfg_file))
                continue

            file_data = yaml.safe_load(cfg_file.read_text(encoding="utf-8"))

            # TODO(rtamalin): Implement a list merge mechanism so that
            # backend lists are merged together rather than the update's
            # backend list replacing the existing backend list contents.
            cfg_data.update(file_data)

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
            self._config_data = CollectorConfig(self._load_config())
        return self._config_data
