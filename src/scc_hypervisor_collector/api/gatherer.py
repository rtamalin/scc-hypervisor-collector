"""
SCC Hypervisor Collector VHGatherer.

The VHGather is a wrapper class for managing virtual-host-gatherer
integration.
"""

from typing import (Any, cast, Dict, Optional, Sequence)

from gatherer.gatherer import Gatherer


class VHGatherer:
    """Wrapper class for the Virtual Host Gatherer."""

    def __init__(self) -> None:

        self._gatherer: Gatherer = Gatherer()
        self._module_params: Optional[Dict[str, Dict]] = None

    @property
    def gatherer(self) -> Gatherer:
        """Read-only gatherer instance."""
        return self._gatherer

    def _load_modules(self) -> None:
        """Call Gatherer.list_modules() to trigger loading worker
        modules if not already done."""
        if self._module_params is None:
            self._module_params = self.gatherer.list_modules()

    @property
    def module_params(self) -> Dict[str, Dict]:
        """Paramaters for all available modules."""
        self._load_modules()

        return cast(Dict[str, Dict], self._module_params)

    @property
    def module_names(self) -> Sequence[str]:
        """The names of the available modules."""
        return tuple(self.module_params.keys())

    def get_module_params(self, module_name: str) -> Dict:
        """Retrieve paramaters for specified module.

        Args:
            module_name (str): The name of the module to lookup.

        Returns:
            Dict: A dictionary of parameters associated with the specified
                module.
        """
        return self.module_params.get(module_name, {})

    def get_worker(self, module_name: str) -> Optional[Any]:
        """Retrieve worker associated with specified module name, if any.

        Args:
            module_name (str): The name of the module to lookup.

        Returns:
            Optional[Any]: The found module, or None if no match was found.
        """
        self._load_modules()

        return self.gatherer.modules.get(module_name, None)
