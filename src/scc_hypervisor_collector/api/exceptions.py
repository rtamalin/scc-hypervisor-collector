"""
SCC Hypervisor Collector Exceptions

The set of exceptions that are raised by the SCC Hypervisor Collector.
"""


# Base exception class
class CollectorException(Exception):
    """Base exception class for scc-hypervisor-collector exceptions."""


# config_manager exceptions
class ConfigManagerException(CollectorException):
    """Base exception class for config manager exceptions."""


class ConfigManagerError(ConfigManagerException):
    """Invalid parameters specified for ConfigManager."""


class EmptyConfigurationError(ConfigManagerException):
    """Empty Configuration loaded error."""


# configuration errors
class NoConfigFilesFoundError(ConfigManagerException):
    """No config files found for specified paramaters error.

    Arguments:
        config_file (str): the config file (if any) specified
        config_dir (str): the config dir specified.
    """

    def __str__(self) -> str:
        return (
            f"{self.args[0]}: "
            f"config_file={self.args[1]!r} "
            f"config_dir={self.args[2]!r}"
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

    Arguments:
        id (str): the id of the backend for which retries failed.
        module (str): the backend module type
        retries (int): the number of retry attempts.
    """

    def __str__(self) -> str:
        return (
            f"{self.args[0]}: "
            f"Backend id={self.args[1]!r}, "
            f"module={self.args[2]!r}, "
            f"retries={self.args[3]!r}"
        )


# scheduler errors
class CollectionSchedulerException(CollectorException):
    """Base exception class for scheduler exceptions."""


class SchedulerInvalidConfigError(CollectionSchedulerException):
    """Invalid configuration provided to scheduler."""


# uploader errors
class SCCUploaderException(CollectorException):
    """Base exception class for uploader exceptions."""
