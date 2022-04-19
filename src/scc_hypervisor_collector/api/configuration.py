"""
SCC Hypervisor Collector Config Content.

The configuration for the SCC Hypervisor Collector is managed
as a hierarchy of dict-like mutable mapping objects which can
be validated against a set of required fields.

Additionally it is possible to specify a list of sensitive fields
whose values should not be displayed when they are rendered as
strings (using str()) or as a representation (using repr()).
"""

from collections.abc import MutableMapping
import logging
from typing import (Any, ClassVar, Dict, Iterator, List, Optional, Set)
import uuid

from .gatherer import VHGatherer
from .exceptions import (BackendConfigError, CollectorConfigContentError)

LOG = logging.getLogger()


# Configuration Data Helper/Wrapper Classes
class GeneralConfig(MutableMapping):
    """A dictionary-like object used to store config settings.

    Takes additional optional arguments specifying the lists of
    required and sensitive config fields, and provides properties
    that can be used to check for validity, and report any fields
    that may be missing, as well as assign new values to the
    required and sensitive fields lists.

    NOTE: Validity checking is non-recursive, checking only the
    validity of this object itself.

    Special keyword arguments:
        _required_fields (Set or List):
            A set or list of fields that must be provided for the
            config to be considered valid.

        _sensitive_fields (Set):
            A set or list of fields whose values should not be
            rendered via str() or repr().

    Special properties:
        required_fields (Set):
            The list of required fields that must be provided for
            the config to be considered valid.

        valid (bool):
            Indicates if the provided config data is valid.

        missing_fields (Set):
            The list of required fields that have not been specified;
            will be empty if valid is True.

        sensitive_fields (Set):
            The list of sensitive fields whose values should not be
            rendered via str() or repr().
    """

    def __init__(self, *args: Any, **kwargs: Any):
        # Initialise our internal config storage as an empty dict
        self._config: Dict = {}

        # Check for a required fields specification
        self._required: Set[str] = set(kwargs.pop('_required_fields', set()))

        # Check for a sensitive fields specification
        self._sensitive: Set[str] = set(kwargs.pop('_sensitive_fields', set()))

        # Update the internal config storage with remaining kwargs fields
        self.update(dict(*args, **kwargs))

        # Validate content
        if not self.valid:
            raise CollectorConfigContentError(
                f"Invalid configuration data provided: {self!r}"
            )

    def __getitem__(self, key: Any) -> Any:
        return self._config[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        self._config[key] = value

    def __delitem__(self, key: Any) -> None:
        del self._config[key]

    def __iter__(self) -> Iterator:
        return iter(self._config)

    def __len__(self) -> int:
        return len(self._config)

    @property
    def required_fields(self) -> Set[str]:
        """Returns a copy of the list of required fields if any.

        Returns:
            Set (str): Required fields
        """
        return set(self._required)

    @property
    def valid(self) -> bool:
        """Indicates whether the provided config is valid, i.e
        contains all the required fields.

        Returns:
            bool: True if all the required fields have been provided
        """
        return all(r in self._config for r in self.required_fields)

    @property
    def missing_fields(self) -> Set[str]:
        """The list of missing fields; will be empty if config is valid.

        Returns:
            Set (str): Set of fields that haven't been provided
        """
        return set({r for r in self._required if r not in self._config})

    @property
    def sensitive_fields(self) -> Set[str]:
        """Returns a copy of the set of sensitive fields if any.

        Returns:
            Set (str): Sensitive fields
        """
        return set(self._sensitive)

    def _sanitized_config(self) -> Dict:
        cfg = dict(self._config)
        for s in self._sensitive:
            if s in cfg:
                cfg[s] = "********"
        return cfg

    def __str__(self) -> str:
        return str(self._sanitized_config())

    def __repr__(self) -> str:
        return repr(self._sanitized_config())


class BackendConfig(GeneralConfig):
    """Hypervisor Backend specific configuration settings management.

    In addition to the special properties provided by 'GeneralConfig',
    this class also provides special 'module' and 'id' properties.
    """

    # List known option fields for all possible backends
    _MODULE_OPTIONAL_FIELDS: ClassVar[Dict[str, Set[str]]] = {
        # AmazonEC2
        "AmazonEC2": set(),

        # Azure
        "Azure": set(),

        # File doesn't appear to have any sensitive fields
        "File": set(),

        # GoogleCE doesn't appear to have any sensitive fields
        "GoogleCE": set(),

        # Kubernetes doesn't appear to have any sensitive fields
        "Kubernetes": set(),

        # Libvirt
        "Libvirt": set((
            "sasl_username",
            "sasl_password",
        )),

        # NutanixAHV
        "NutanixAHV": set(),

        # VMware
        "VMware": set(),
    }

    # List known sensitive fields for all possible backends
    _MODULE_SENSITIVE_FIELDS: ClassVar[Dict[str, Set[str]]] = {
        # AmazonEC2
        "AmazonEC2": set((
            "secret_access_key",
        )),

        # Azure
        "Azure": set((
            "secret_key",
        )),

        # File doesn't appear to have any sensitive fields
        "File": set(),

        # GoogleCE doesn't appear to have any sensitive fields
        "GoogleCE": set(),

        # Kubernetes doesn't appear to have any sensitive fields
        "Kubernetes": set(),

        # Libvirt
        "Libvirt": set((
            "sasl_password",
        )),

        # NutanixAHV
        "NutanixAHV": set((
            "password",
        )),

        # VMware
        "VMware": set((
            "password",
        )),
    }

    def __init__(self, *args: Any, **kwargs: Any):

        # Each backend config gets it's own instance of VHGatherer
        self._gatherer: VHGatherer = VHGatherer()

        # Create a dict from the provided arguments
        combined_args = dict(*args, **kwargs)

        # Retrieve the module specified in the arguments, if any
        module = combined_args.get('module', None)
        if module is None:
            raise BackendConfigError(
                    "A backend config must have a 'module' entry"
                  )

        # Lookup the worker module entry in the gatherer modules
        self._worker: Optional[Any] = self._gatherer.get_worker(module)
        LOG.debug("module %s -> worker %s", repr(module), repr(self._worker))
        if self._worker is None:
            supported_modules = self._gatherer.module_names
            raise BackendConfigError(
                    f"Specified backend module {module!r} is not one of "
                    f"the supported modules: {supported_modules!r}"
                  )

        self._worker_params: Dict = self._gatherer.get_module_params(module)

        # if an id hasn't been specified in the combined_args then add one
        if 'id' not in combined_args:
            combined_args['id'] = str(uuid.uuid4())

        # use params specified for gatherer module as required fields,
        # excluding any optional fields.
        required: Set[str] = set(self._worker_params.keys()).difference(
            self._MODULE_OPTIONAL_FIELDS[module]
        )

        # use known sensitive fields associated with module name
        sensitive: Set[str] = self._MODULE_SENSITIVE_FIELDS[module]

        super().__init__(_required_fields=required,
                         _sensitive_fields=sensitive,
                         **combined_args)

        LOG.debug("Required fields: %s", repr(self.required_fields))
        LOG.debug("Sensitive fields: %s", repr(self.sensitive_fields))
        LOG.debug("Missing fields: %s", repr(self.missing_fields))

    @property
    def gatherer(self) -> Optional[VHGatherer]:
        """Read-only gatherer instance associated with backend."""

        return self._gatherer

    @property
    def module(self) -> str:
        """The backend module name."""

        return self['module']

    @property
    def id(self) -> str:
        """Read-only id of the hypervisor backend config."""

        return self['id']

    @property
    def worker(self) -> Any:
        """The virtual-host-gatherer worker associated with the
        module specified in the config settings."""

        return self._worker

    @property
    def worker_params(self) -> Dict:
        """The parameters supported by the worker associated with
        the module specified in the config settings."""

        return self._worker_params


class SccCredsConfig(GeneralConfig):
    """Hypervisor Collector SCC credentials settings.

    The SCC credentials configuration settings hold the following
    settings:
      * username
      * password

    Read-only properties are defined for each setting.

    Special properties:
        username: The SCC Account username
        password: The SCC Account password
    """

    def __init__(self, *args: Any, **kwargs: Any):

        self._module: Optional[Any] = None

        required: Set[str] = set((
            "username",
            "password",
        ))
        sensitive: Set[str] = set((
            "password",
        ))

        super().__init__(_required_fields=required,
                         _sensitive_fields=sensitive,
                         *args, **kwargs)

    @property
    def username(self) -> str:
        """The SCC Account Username."""

        return self['username']

    @property
    def password(self) -> str:
        """The SCC Account password."""

        return self['password']


class CredentialsConfig(GeneralConfig):
    """Hypervisor Collector credentials configuration settings.

    The credentials configuration consists of the following
    credential sections:
      * scc

    Read-only properties are defined for each credential section.

    Special properties:
        scc: The SCC credentials to use.
    """

    def __init__(self, *args: Any, **kwargs: Any):

        self._module: Optional[Any] = None

        required: Set[str] = set((
            "scc",
        ))
        sensitive: Set[str] = set((
            # No sensitive fields in the credentials config itself
        ))

        # Create a dict from the provided arguments
        combined_args = dict(*args, **kwargs)

        # Ensure the SCC credentials are managed by a SCCCredsConfig object
        combined_args["scc"] = SccCredsConfig(combined_args["scc"])

        super().__init__(_required_fields=required,
                         _sensitive_fields=sensitive,
                         **combined_args)

    @property
    def scc(self) -> SccCredsConfig:
        """The SCC Credentials."""
        # return a lightweight copy of the SCC creds
        return SccCredsConfig(self['scc'])


class CollectorConfig(GeneralConfig):
    """Hypervisor Collector main confguration.

    The main configuration consists of the following sections:
      * credentials
      * backends

    Read-only properties have been defined for each configuration
    section.

    The credentials section holds the credentials needed by the
    command, such as the SCC credentials used to upload any data
    collected about the backends to the SCC.

    The backends section holds a list of configured backends and
    the associated backend specific settings required to run queries
    against the specified backend.

    Special properties:
        credentials: A CredentialsConfig object holding the credentials
            specified in the configuration.
        backends: A list of BackendConfig objects holding the backend
            specific settings.
    """

    def __init__(self, *args: Any, **kwargs: Any):

        self._module: Optional[Any] = None

        required: Set[str] = set((
            "backends",
            "credentials",
        ))
        sensitive: Set[str] = set((
            # No sensitive fields in the top level config
        ))

        # Create a dict from the provided arguments
        combined_args = dict(*args, **kwargs)

        # Ensure the credentials are managed by a credentials object
        combined_args["credentials"] = CredentialsConfig(
            combined_args["credentials"]
        )

        # ensure all backends are managed by BackendConfig objects
        combined_args["backends"] = [
            BackendConfig(b) for b in combined_args["backends"]
        ]

        super().__init__(_required_fields=required,
                         _sensitive_fields=sensitive,
                         **combined_args)

    @property
    def backends(self) -> List[BackendConfig]:
        """The list of backends specified in the config.

        Returns:
            List (BackendConfig): A list of BackendConfig objects
        """
        # return a lightweight copy of the backends config
        return list(self['backends'])

    @property
    def credentials(self) -> CredentialsConfig:
        """The configured credentials.

        Returns:
            CredentialsConfig: The configured credentials.
        """
        # return a lightweight copy of the credentials config
        return CredentialsConfig(self['credentials'])
