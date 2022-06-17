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

from .gatherer import VHGatherer
from .exceptions import (BackendConfigError, CollectorConfigContentError)


# Configuration Data Helper/Wrapper Classes
class GeneralConfig(MutableMapping):
    """A dictionary-like object used to store config settings.

    Takes additional optional arguments specifying the lists of
    required and sensitive config fields, and provides properties
    that can be used to check for validity, and report any fields
    that may be missing, as well as assign new values to the
    required and sensitive fields lists.

    Special keyword arguments:
        _required_fields (Set or List):
            A set or list of fields that must be provided for the
            config to be considered valid.

        _sensitive_fields (Set):
            A set or list of fields whose values should not be
            rendered via str() or repr().

        _check (bool):
            A mode to validate the configuration. Default is false

        _config_errors (List)
            A list of configuration errors. Default is empty

        _children (List)
            A list of child objects. Default is empty

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

        config_errors (List):
            The list of errors for the given configuration.

        children (List):
            The list of child objects.

    """

    def __init__(self, *args: Any, **kwargs: Any):
        # Initialise our internal config storage as an empty dict
        self._config: Dict = {}

        # Check for a required fields specification
        self._required: Set[str] = set(kwargs.pop('_required_fields', set()))

        # Check for a sensitive fields specification
        self._sensitive: Set[str] = set(kwargs.pop('_sensitive_fields', set()))

        self._check: bool = kwargs.pop('_check', False)

        self._config_errors: List = kwargs.pop('_config_errors', [])

        self._children: List = kwargs.pop('_children', [])

        self._log = logging.getLogger(__name__ + '.GeneralConfig')

        try:
            # Update the internal config storage with remaining kwargs fields
            self.update(dict(*args, **kwargs))
        except TypeError as type_error:
            if not self._check:
                raise type_error

        # Validate content
        if not self.valid:
            msg = f"Invalid configuration data provided: {self!r}"
            self._log.error(msg)
            if not self._check:
                raise CollectorConfigContentError(msg)

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

        children_valid = all(c.valid for c in self._children)

        req_fields_found = all(r in self._config for r in self.required_fields)

        return all([req_fields_found, children_valid,
                    len(self._config_errors) == 0])

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

    @property
    def config_errors(self) -> List[str]:
        """Return the list of identified config errors"""
        return self._config_errors.copy()

    @property
    def children(self) -> List[str]:
        """Return the list of children"""
        return self._children.copy()

    @property
    def logger(self) -> logging.Logger:
        """Return the logger object"""
        return self._log

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
        self._check = kwargs.pop('_check', False)
        self._config_errors = []
        self._log = logging.getLogger(__name__ + '.BackendConfig')

        # Create a dict from the provided arguments
        combined_args = dict(*args, **kwargs)

        # Make the 'id' attribute for the backend required
        backend_id = combined_args.get('id', None)
        if backend_id is None:
            msg = "Invalid backend - missing required field: id"
            self._log.error(msg)
            raise BackendConfigError(msg)

        # Retrieve the module specified in the arguments, if any
        module = combined_args.get('module', None)
        if module is None:
            msg = f"Invalid backend {combined_args['id']!r} - " \
                  f"missing required field: module"
            self._log.error(msg)
            raise BackendConfigError(msg)

        # Lookup the worker module entry in the gatherer modules
        self._worker: Optional[Any] = self._gatherer.get_worker(module)
        self._log.debug("module %s -> worker %s", repr(module),
                        repr(self._worker))
        if self._worker is None:
            supported_modules = self._gatherer.module_names
            msg = f"Invalid backend {combined_args['id']!r} - " \
                  f"module {module!r} is not one of the supported modules: " \
                  f"{supported_modules!r}"
            self._log.error(msg)
            raise BackendConfigError(msg)

        self._worker_params: Dict = self._gatherer.get_module_params(module)

        # use params specified for gatherer module as required fields,
        # excluding any optional fields.
        required: Set[str] = set(self._worker_params.keys()).difference(
            self._MODULE_OPTIONAL_FIELDS[module]
        )

        # use known sensitive fields associated with module name
        sensitive: Set[str] = self._MODULE_SENSITIVE_FIELDS[module]

        super().__init__(_required_fields=required,
                         _sensitive_fields=sensitive,
                         _check=self._check,
                         _config_errors=self._config_errors,
                         _children=[],
                         **combined_args)
        self._log.debug("Required fields: %s", repr(self.required_fields))
        self._log.debug("Sensitive fields: %s", repr(self.sensitive_fields))
        self._log.debug("Missing fields: %s", repr(self.missing_fields))

        if not self.valid:
            msg = f"Invalid backend {combined_args['id']!r} " \
                  f"- missing required field: {self.missing_fields!r}"
            self._config_errors.append(msg)
            self._log.error(msg)
            if not self._check:
                raise BackendConfigError(msg)

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
        self._check = kwargs.pop('_check', False)
        self._config_errors = []
        self._log = logging.getLogger(__name__ + '.SccCredsConfig')

        required: Set[str] = set((
            "username",
            "password",
        ))
        sensitive: Set[str] = set((
            "password",
        ))

        super().__init__(_required_fields=required,
                         _sensitive_fields=sensitive,
                         _check=self._check,
                         _config_errors=self._config_errors,
                         _children=[],
                         *args, **kwargs)

        if not self.valid:
            msg = "Invalid scc section"
            if self.missing_fields:
                msg = msg + \
                      f" - missing required fields: {self.missing_fields!r}"
            self._config_errors.append(msg)
            self._log.error(msg)
            if not self._check:
                raise CollectorConfigContentError(msg)

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
        self._check = kwargs.pop('_check', False)
        self._config_errors = []
        self._children = []
        self._log = logging.getLogger(__name__ + '.CredentialsConfig')

        required: Set[str] = set((
            "scc",
        ))
        sensitive: Set[str] = set((
            # No sensitive fields in the credentials config itself
        ))

        combined_args = {}
        try:
            combined_args = dict(*args, **kwargs)
        except TypeError:
            msg = "Missing scc section in credentials"
            self._config_errors.append(msg)
            self._log.error(msg)
            combined_args["scc"] = {}

        # Ensure the SCC credentials are managed by a SCCCredsConfig object
        scc_creds_config = SccCredsConfig(
            combined_args["scc"], _check=self._check)
        combined_args["scc"] = scc_creds_config
        self._config_errors.extend(scc_creds_config.config_errors)
        self._children.append(scc_creds_config)

        super().__init__(_required_fields=required,
                         _sensitive_fields=sensitive,
                         _check=self._check,
                         _config_errors=self._config_errors,
                         _children=self._children,
                         **combined_args)

        if not self.valid:
            msg = "Missing scc section"
            if self.missing_fields:
                msg = msg + \
                      f" - missing required fields: {self.missing_fields!r}"
            if not self._check:
                raise CollectorConfigContentError(msg)

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
        self._check = kwargs.pop('_check', False)
        self._config_errors = []
        self._children = []
        self._log = logging.getLogger(__name__ + '.CollectorConfig')

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
        try:
            creds_config = CredentialsConfig(
                combined_args["credentials"], _check=self._check
            )
            combined_args["credentials"] = creds_config
            self._config_errors.extend(creds_config.config_errors)
            self._children.append(creds_config)
        except (KeyError, TypeError, CollectorConfigContentError) as error:
            if isinstance(error, KeyError):
                msg = f"Missing {error} section"
            else:
                msg = f"{error}"
            self._log.error(msg)
            self._config_errors.append(msg)
            if not self._check:
                raise error
        self.check_for_backends(combined_args)
        try:
            for i, b in enumerate(combined_args["backends"]):
                try:
                    errors = []
                    backend_config = BackendConfig(b, _check=self._check)
                    combined_args["backends"][i] = backend_config
                    errors.extend(backend_config.config_errors)
                    self._children.append(backend_config)
                except BackendConfigError as e:
                    self._config_errors.append(str(e))
                    if not self._check:
                        raise e
                self._config_errors.extend(errors)
        except KeyError as error:
            msg = f"Missing {error} section"
            self._config_errors.append(msg)
            self._log.error(msg)
            if not self._check:
                raise error
        except TypeError as error:
            msg = "Invalid backends section"
            self._config_errors.append(msg)
            self._log.error(msg)
            if not self._check:
                raise TypeError(msg) from error

        super().__init__(_required_fields=required,
                         _sensitive_fields=sensitive,
                         _check=self._check,
                         _config_errors=self._config_errors,
                         _children=self._children,
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

    def check_for_backends(self, combined_args: Dict) -> None:
        """ check if the configuration has the backends entry"""
        if not combined_args.get("backends"):
            msg = "No backends specified in config!"
            self._log.error(msg)
            self._config_errors.append(msg)
            if not self._check:
                raise BackendConfigError(msg)
