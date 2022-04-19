"""
SCC Hypervisor Collector API.

This package implements the API for the SCC Hypervisor Collector.
"""

from .exceptions import (
    BackendConfigError,
    CollectorException,
    CollectorConfigContentError,
    CollectorConfigurationException,
    CollectionSchedulerException,
    HypervisorCollectorException,
    HypervisorCollectorRetriesExhausted,
    GathererException,
    NoConfigFilesFoundError,
    SCCUploaderException,
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
    'CollectorException',
    'CollectorConfigurationException',
    'CollectorConfigContentError',
    'CollectionSchedulerException',
    'HypervisorCollectorException',
    'HypervisorCollectorRetriesExhausted',
    'GathererException',
    'NoConfigFilesFoundError',
    'SCCUploaderException',

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
