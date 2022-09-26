"""
SCC Hypervisor Collector CollectionScheduler

The CollectionScheduler is responsible for scheduling the requests
to retrieve the hypervisor details from the specified backends, using
the provided backend settings.
"""

import logging
from pathlib import Path
from typing import (Dict, List, Optional, Sequence, Set)
import yaml

from .configuration import CollectorConfig
from .exceptions import (
    CollectionResultsInvalidData,
    ResultsFilePermissionsError,
    SchedulerInvalidConfigError,
)
from .hypervisor_collector import HypervisorCollector
from .util import check_permissions


class CollectionResults:
    """Manage the set of results for a scheduler run.

    Can be used to save out a copy of the results to be loaded later,
    or to load a set of results to be used as the data to be uploaded.
    """

    def __init__(self, scheduler: Optional['CollectionScheduler'] = None):
        self._results: List = []
        if scheduler:
            self._get_results_from_scheduler(scheduler)

    @property
    def results(self) -> List:
        """Return a copy of the results"""
        return self._results.copy()

    def _get_results_from_scheduler(self,
                                    scheduler: 'CollectionScheduler') -> None:
        """Generate results content using provided scheduler."""

        self._results = [
            dict(backend=hv.backend.id, details=hv.details,
                 valid=hv.succeeded)
            for hv in scheduler.hypervisors
        ]

    def save(self, file_path: Path) -> None:
        """Save the results to the specified file."""
        # create the results file if it doesn't already exist, and ensure
        # that only user access is permitted.
        if not file_path.exists():
            file_path.touch(mode=0o600)
        else:
            file_path.chmod(mode=0o600)

        # write the managed results to the specified file
        with file_path.open("w", encoding="utf-8") as fp:
            yaml.safe_dump(self._results, fp)

        # validate the file permissions after writing to it
        check_permissions(file_path, fail_exc=ResultsFilePermissionsError)

    def load(self, file_path: Path) -> None:
        """Load the result from the specified file."""
        # validate the file permissions before reading from it
        check_permissions(file_path, fail_exc=ResultsFilePermissionsError)

        # read the file contents and validate basic structure
        with file_path.open("r", encoding="utf-8") as fp:
            results = yaml.safe_load(fp)

        # Perform some basic validity checking on the results content
        results_valid = True
        if not isinstance(results, list):
            results_valid = False
        elif not all(('backend' in e) and ('valid' in e)
                     for e in results):
            results_valid = False
        elif not all('details' in e
                     for e in results
                     if e['valid']):
            results_valid = False

        # Fail if validity checks fail
        if not results_valid:
            raise CollectionResultsInvalidData(
                'Specified results file contents are invalid'
            )

        # store loaded data as the results to be managed
        self._results = results


class CollectionScheduler:
    """Collection Scheduler for scc-hypervisor-collector.

    Given a configuration as argument the scheduler will group the
    specified backends by type, instantiating a HypervisorCollector
    for each and schedule the collection of backend details.

    Special Properties:
        config (CollectorConfig): the configuration provided to the
            scheduler.

        hypervisor_types (Set[str]): the set of hypervisor backend
            types that are found in the configuration.

        hypervisor_groups (Dict[str, Sequence[HypervisorCollector]]):
            the hypervisor backend collectors grouped by backend type.

        hypervisors (Sequence[HypervisorCollector]): the list of collectors
            instantiated; one for the backend specified in the provided
            configuration.

    Special Methods:
        run(): Run the backend queries on all of the configured collectors.
    """

    def __init__(self, config: CollectorConfig):
        """Schedule collection of details from config specified backends."""
        self._log = logging.getLogger(__name__)

        self._log.debug("config=%s", repr(config))

        # sanity check the parameters
        if config is None:
            raise SchedulerInvalidConfigError(
                "No configuration provided!"
            )

        if not config.backends:
            raise SchedulerInvalidConfigError(
                "No backends specified in config!"
            )

        # save the parameters
        self._config: CollectorConfig = config

        # determine set of hypervisor types specified in configuration
        self._hypervisor_types: Set[str] = {b.module for b in config.backends}

        self._log.debug("hv_types: %s", repr(self._hypervisor_types))

        # instantiate collectors for each backend
        self._hypervisors: Sequence[HypervisorCollector] = [
            HypervisorCollector(b) for b in config.backends
        ]

        self._log.debug("hvs: %s", repr(self._hypervisors))

        # group collectors by hypervisor type
        self._hypervisor_groups: Dict[str, Sequence[HypervisorCollector]] = {
            t: [h for h in self._hypervisors if h.backend.module == t]
            for t in self._hypervisor_types
        }

        # collected results
        self._results: Optional[CollectionResults] = None

        self._log.debug("hv_groups: %s", repr(self._hypervisor_groups))

    def _run_hv_type_queries(self, hv_type: str) -> None:
        """Query backends for each configured hypervisor of given type."""
        for hv_collector in self._hypervisor_groups[hv_type]:
            hv_collector.run()

    def run(self) -> None:
        """Run the hypervisor queries on a per-type basis."""
        for hv_type in self.hypervisor_types:
            self._run_hv_type_queries(hv_type)

    @property
    def config(self) -> CollectorConfig:
        """The configuration that we are scheduling collection for."""
        return self._config

    @property
    def hypervisor_types(self) -> Set[str]:
        """The hypervisor types found in the configured backends."""
        return self._hypervisor_types

    @property
    def hypervisor_groups(self) -> Dict[str, Sequence[HypervisorCollector]]:
        """HypervisorCollectors associated with configured backends."""
        return dict(self._hypervisor_groups)

    @property
    def hypervisors(self) -> Sequence[HypervisorCollector]:
        """HypervisorCollectors associated with configured backends."""
        return tuple(self._hypervisors)

    @property
    def results(self) -> CollectionResults:
        """Return the collected results instance."""
        if self._results is None:
            self._results = CollectionResults(scheduler=self)
        return self._results
