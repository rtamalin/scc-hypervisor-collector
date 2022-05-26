"""
SCC Hypervisor Collector API.

This package implements the API for the SCC Hypervisor Collector.
"""

from .exceptions import (
    BackendConfigError,
    ConfigManagerError,
    ConfigManagerException,
    ConflictingBackendsError,
    CollectorException,
    CollectorConfigContentError,
    CollectorConfigurationException,
    CollectionSchedulerException,
    EmptyConfigurationError,
    HypervisorCollectorException,
    HypervisorCollectorRetriesExhausted,
    GathererException,
    NoConfigFilesFoundError,
    SCCUploaderException,
    SchedulerInvalidConfigError
)
from .config_manager import ConfigManager
from .configuration import (BackendConfig, CollectorConfig, CredentialsConfig,
                            GeneralConfig, SccCredsConfig)
from .gatherer import VHGatherer
from .hypervisor_collector import HypervisorCollector
from .scheduler import CollectionScheduler
from .uploader import SCCUploader

__all__ = [
    # exceptions
    'BackendConfigError',
    'ConfigManagerError',
    'ConflictingBackendsError',
    'CollectorException',
    'CollectorConfigurationException',
    'CollectorConfigContentError',
    'CollectionSchedulerException',
    'ConfigManagerException',
    'EmptyConfigurationError',
    'HypervisorCollectorException',
    'HypervisorCollectorRetriesExhausted',
    'GathererException',
    'NoConfigFilesFoundError',
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

    # scheduler
    'CollectionScheduler',

    # scc_uploader
    'SCCUploader',
]
