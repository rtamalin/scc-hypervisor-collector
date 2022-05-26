"""
SCC Hypervisor Collector Exceptions

The set of exceptions that are raised by the SCC Hypervisor Collector.
"""

from typing import Any


# Base exception class
class CollectorException(Exception):
    """Base exception class for scc-hypervisor-collector exceptions.

    Basic Arguments:
        message (str): the message
    """

    def _get_arg(self, index: int, default: Any = None) -> Any:
        """Retrieve self.args[index] or return default."""
        if index < len(self.args):
            return self.args[index]
        return default

    @property
    def message(self) -> Any:
        """Retrieves the message argument."""
        return self._get_arg(0)


# config_manager exceptions
class ConfigManagerException(CollectorException):
    """Base exception class for config manager exceptions."""


class ConfigManagerError(ConfigManagerException):
    """Invalid parameters specified for ConfigManager."""


class ConflictingBackendsError(ConfigManagerException):
    """Conflicting backends specified in config.

    Additional Arguments:
        backend_ids (list): the config file (if any) specified
    """

    @property
    def backend_ids(self) -> Any:
        """Retrieves the backend_ids argument."""
        return self._get_arg(1)


class EmptyConfigurationError(ConfigManagerException):
    """Empty Configuration loaded error."""


# configuration errors
class NoConfigFilesFoundError(ConfigManagerException):
    """No config files found for specified paramaters error.

    Additional Arguments:
        config_file (str): the config file (if any) specified
        config_dir (str): the config dir specified.
    """

    @property
    def config_file(self) -> Any:
        """Retrieves the config_file argument."""
        return self._get_arg(1)

    @property
    def config_dir(self) -> Any:
        """Retrieves the config_dir argument."""
        return self._get_arg(2)

    def __str__(self) -> str:
        return (
            f"{self.message}: "
            f"config_file={self.config_file!r} "
            f"config_dir={self.config_dir!r}"
        )


# configuration errors
class CollectorConfigurationException(CollectorException):
    """Base exception class for configuration exceptions."""


class CollectorConfigContentError(CollectorConfigurationException):
    """Configuration content error."""


class BackendConfigError(CollectorConfigurationException):
    """Backend config error."""


# gatherer errors
class GathererException(CollectorException):
    """Base exception class for gatherer exceptions."""


# hypervisor_collector errors
class HypervisorCollectorException(CollectorException):
    """Base exception class for hypervisor_collector exceptions."""


class HypervisorCollectorRetriesExhausted(HypervisorCollectorException):
    """Repeated gather backend module queries failed to retrieve results.

    Additional Arguments:
        id (str): the id of the backend for which retries failed.
        module (str): the backend module type
        retries (int): the number of retry attempts.
    """

    @property
    def backend_id(self) -> Any:
        """Retrieves the backend_id argument."""
        return self._get_arg(1)

    @property
    def modules(self) -> Any:
        """Retrieves the module argument."""
        return self._get_arg(2)

    @property
    def retries(self) -> Any:
        """Retrieves the retries argument."""
        return self._get_arg(3)

    def __str__(self) -> str:
        return (
            f"{self.message}: "
            f"Backend id={self.backend_id!r}, "
            f"module={self.modules!r}, "
            f"retries={self.retries!r}"
        )


# scheduler errors
class CollectionSchedulerException(CollectorException):
    """Base exception class for scheduler exceptions."""


class SchedulerInvalidConfigError(CollectionSchedulerException):
    """Invalid configuration provided to scheduler."""


# uploader errors
class SCCUploaderException(CollectorException):
    """Base exception class for uploader exceptions."""
