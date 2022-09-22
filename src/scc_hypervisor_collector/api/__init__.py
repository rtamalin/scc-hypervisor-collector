"""
SCC Hypervisor Collector API.

This package implements the API for the SCC Hypervisor Collector.
"""

from .exceptions import (
    BackendConfigError,
    ConfigManagerError,
    ConfigManagerException,
    ConflictingBackendsError,
    CollectionResultsInvalidData,
    CollectionSchedulerException,
    CollectorException,
    CollectorConfigContentError,
    CollectorConfigurationException,
    CollectorUtilException,
    EmptyConfigurationError,
    FilePermissionsError,
    HypervisorCollectorException,
    GathererException,
    NoConfigFilesFoundError,
    ResultsFilePermissionsError,
    SCCUploaderException,
    SchedulerInvalidConfigError,
)
from .config_manager import ConfigManager
from .configuration import (BackendConfig, CollectorConfig, CredentialsConfig,
                            GeneralConfig, SccCredsConfig)
from .gatherer import VHGatherer
from .hypervisor_collector import HypervisorCollector, HypervisorDetails
from .scheduler import CollectionResults, CollectionScheduler
from .uploader import SCCUploader
from .util import check_permissions

__all__ = [
    # exceptions
    'BackendConfigError',
    'ConfigManagerError',
    'ConflictingBackendsError',
    'CollectionResultsInvalidData',
    'CollectionSchedulerException',
    'CollectorException',
    'CollectorConfigurationException',
    'CollectorConfigContentError',
    'CollectorUtilException',
    'ConfigManagerException',
    'EmptyConfigurationError',
    'FilePermissionsError',
    'HypervisorCollectorException',
    'GathererException',
    'NoConfigFilesFoundError',
    'ResultsFilePermissionsError',
    'SCCUploaderException',
    'SchedulerInvalidConfigError',

    # config_manager
    'ConfigManager',

    # configuration
    'BackendConfig',
    'CollectorConfig',
    'CredentialsConfig',
    'GeneralConfig',
    'SccCredsConfig',

    # gatherer
    "VHGatherer",

    # hypervisor_collector
    'HypervisorCollector',
    'HypervisorDetails',

    # scheduler
    'CollectionResults',
    'CollectionScheduler',

    # uploader
    'SCCUploader',

    # util
    'check_permissions',
]
