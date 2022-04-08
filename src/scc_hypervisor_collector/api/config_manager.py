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

LOG = logging.getLogger()


class ConfigManager:
    """Configuration Management for scc-hypervisor-collector"""

    def __init__(self, config_file: Optional[str] = None,
                 config_dir: Optional[str] = None):
        """Initialiser for ConfigManager"""

        LOG.debug("config_file=%s", repr(config_file))
        LOG.debug("config_dir=%s", repr(config_dir))

        # Lazy loaded configuration data
        self._config_data: Optional[Dict] = None

        # List of potential config sources
        self._config_files: List = []

        # Save parameters, converting to Path objects if specified.
        self._config_file: Optional[Path] = (
            Path(config_file) if config_file else None
        )
        self._config_dir: Optional[Path] = (
            Path(config_dir) if config_dir else None
        )

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

        # If a config file was specified then append it to the sorted
        # list of found files ensuring it's contents will supercede
        # previous config settings
        if self._config_file:
            cfg_files.append(self._config_file)

        return cfg_files

    def _load_config(self) -> Dict:
        """Load the specified config files, if any, merging content
        together.
        Returns:
            Dict: The (possibly empty) dictionary of config data.
        """

        cfg_data = {}
        for cfg_file in self._config_files:
            if not cfg_file.exists():
                continue

            file_data = yaml.safe_load(cfg_file.read_text(encoding="utf-8"))
            cfg_data.update(file_data)

        return cfg_data

    @property
    def config_files(self) -> List:
        """Return the list of identified config files."""
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
    def config_data(self) -> Optional[Dict]:
        """Return the config_data loaded from the specifed config
           sources."""
        if self._config_data is None:
            self._config_data = self._load_config()
        return self._config_data
