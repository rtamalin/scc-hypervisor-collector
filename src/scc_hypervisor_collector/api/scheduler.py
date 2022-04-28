"""
SCC Hypervisor Collector CollectionScheduler

The CollectionScheduler is responsible for scheduling the requests
to retrieve the hypervisor details from the specified backends, using
the provided backend settings.
"""

import logging
from typing import (Dict, Sequence, Set)

from .configuration import CollectorConfig
from .exceptions import SchedulerInvalidConfigError
from .hypervisor_collector import HypervisorCollector

LOG = logging.getLogger()


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

        LOG.debug("config=%s", repr(config))

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

        LOG.debug("hv_types: %s", repr(self._hypervisor_types))

        # instantiate collectors for each backend
        self._hypervisors: Sequence[HypervisorCollector] = [
            HypervisorCollector(b) for b in config.backends
        ]

        LOG.debug("hvs: %s", repr(self._hypervisors))

        # group collectors by hypervisor type
        self._hypervisor_groups: Dict[str, Sequence[HypervisorCollector]] = {
            t: [h for h in self._hypervisors if h.backend.module == t]
            for t in self._hypervisor_types
        }

        LOG.debug("hv_groups: %s", repr(self._hypervisor_groups))

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
