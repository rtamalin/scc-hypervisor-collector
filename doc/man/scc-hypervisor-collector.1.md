---
title: SCC-HYPERVISOR-COLLECTOR
section: 1
header: SCC Hypervisor Collector
date: June 2022
---
# NAME
**scc-hypervisor-collector** - Collect & Upload Hypervisor details
to SUSE Customer Center

# SYNOPSIS

**scc-hypervisor-collector [<optional>...]**

# DESCRIPTION

The **scc-hypervisor-collector** collects details that are relevant
to SUSE Customer Center (SCC) subscription compliance tracking, from
the specified hypervisors.

The collected details include the total system RAM, CPU architecture
and topology of the hypervisor nodes themselves, as well as the UUIDs
and state (running or shutoff) for the hosted VMs.

## HYPERVISOR DETAILS RETRIEVAL

The **gatherer** Python module provided by the **virtual-host-gatherer(1)**
command is used to retrieve the details from the configured hypervisors.

# OPTIONS

  **-c**, **--config <CONFIG_FILE>**
  : Specifies a YAML file containing configuration settings.

  **--config_dir**, **--config-dir <CONFIG_DIR>**
  : Specifies a directory containing YAML configuration files that
    will be merged together, in lexical sort order, to construct the
    configuration settings.
    Defaults to **~/.config/scc-hypervisor-collector**.

  **-C**, **--check**
  : Checks the specified configuration settings for correctness, reporting
    any issues found.

  **-h**, **--help**
  : Provides basic details about the available command line options.

  **-q**, **--quiet**
  : Runs in quiet mode, only reporting errors.

  **-v**, **--verbose**
  : Runs in verbose mode, reporting additional details.

  **-V**, **--version**
  : Reports the version of **scc-hypervisor-collector**.

  **-L**, **--logfile <LOG_FILE>**
  : Specifies the path to the log file in which to write log messages.
    Defaults to **~/scc-hypervisor-collector.log**.

# SECURITY CONSIDERATIONS

The **scc-hypervisor-collector(1)** is intended to be run from a
restricted service account with no special privileges, and will
exit immediately if it detects that it is running with superuser
privileges.

## CONFIGURATION SETTINGS PERMISSIONS
As the **scc-hypervisor-collector(5)** configuration settings
will contain sensitive information such as passwords, the command
requires that all specified configuration files and directories
must be owned by the non-root user that is running the command,
with restrictive permissions allowing only that user to access
those files.

## TLS/SSL CERTIFICATES

The **virtual-host-gatherer(1)** framework doesn't currently
permit the specification of certs that can be used to validate
connections to the specified hypervisors.

As such any certs that may be needed to securely connect to the
specified hypervisors will need to be registered with the system
certificate stores. See **update-ca-certificates(8)** for details.

# SYSTEMD INTEGRATION

The **scc-hypervisor-collector** package, when installed, automatically
creates the **scchvc** restricted service account, if it doesn't already
exist, with a home directory of **/var/lib/scchvc**.

Additionally two **systemd(1)** units are also installed:

* **scc-hypervisor-collector.service(8)** runs the **scc-hypervisor-collector**
  as the **scchvc** user if a valid configuration has been specified in
  the **scchvc** user account.

* **scc-hypervisor-collector.timer(8)** triggers the
  **scc-hypervisor-collector.service(8)** unit to be run on a daily
  basis by default.

# CONFIGURATION SETTINGS

Configuration settings are specified in YAML format and must contain:

* a list of hypervisor **backends** from which to retrieve relevant
  details
* a collection of **credentials** that will be used to upload the
  collected details to the SUSE Customer Center.

See **scc-hypervisor-collector(5)** for details about the possible
configuration settings.

## CONFIGURATION MANAGEMENT
The configuration settings can be specified in a single YAML file,
or as a set of YAML files whose content will be merged together in
lexical sort order.

The latter scheme allows the configuration settings to be split up
into multiple files, e.g. credentials can be specified in one file,
and the hypervisor backends in one or more files.

When splitting the hypervisor backend details among multiple files,
the **backends** lists in each file will be merged together to form
a single combined list; exact duplicates will be ignored but partial
duplicates will result in errors.

## ACCESS AND OWNERSHIP
For security reasons only the non-root user that is running the
**scc-hypervisor-collector** command should be able to access the
specified configuration files.

## CONFIGURATION VALIDATION
The **--check** option can be utilised to check if the specified
configuration settings are valid, or will report any errors that
it detected.

## SUPPORTED HYPERVISORS

The following hypervisor types are supported:

* VMWare vCenter (type **VMware**)
* Libvirt (type **Libvirt**)

Each hypervisor type has specific configuration settings that must
be provided to permit the relevant details to be retrieved; these
settings are documented in **scc-hypervisor-collector(5)**.

# EXIT CODES

**scc-hypervisor-collector** sets the following exit codes:

* 0:  Run completed successfully, or configuration settings
      are valid if check mode (**--check**) was specified.
* 1:  An error occurred.

# IMPLEMENTATION

**scc-hypervisor-collector(1)** is implemented in Python.
It communicates with the SUSE Customer Center via a RESTful
JSON API over HTTP using TLS encryption.

# ENVIRONMENT

**scc-hypervisor-collector(1)** respects the HTTP_PROXY environment
variable.  See https://www.suse.com/support/kb/doc/?id=000017441 for
more details on how to manually configure proxy usage.

# FILES AND DIRECTORIES

**~/.config/scc-hypervisor-collector/**
: Default configuration directory containing YAML configuration files,
  merged together in lexical sort order.

**~/scc-hypervisor-collector.log**
: Default log file which will be automatically rotated and compressed
  if it gets too large.

**/var/lib/scchvc/.config/scc-hypervisor-collector/**
: Configuration directory that the **scc-hypervisor-collector.service(8)**
  checks for configuration settings.

**/var/lib/scchvc/scc-hypervisor-collector.log**
: The log file used by the **scc-hypervisor-collector.service(8)**.
  
# AUTHORS

Originally developed by Fergal Mc Carthy (fmccarthy@suse.com) and
Meera Belur (mbelur@suse.com) for the SCC at SUSE LLC (scc-feedback@suse.de)

# LINKS

SUSE Customer Center: https://scc.suse.com

scc-hypervisor-collector on GitHub: https://github.com/SUSE/scc-hypervisor-collector

virtual-host-gatherer on GitHub: https://github.com/uyuni-project/virtual-host-gatherer

YAML Specification: https://yaml.org/

# SEE ALSO

**scc-hypervisor-collector(5)**, **scc-hypervisor-collector.service(8)**, **scc-hypervisor-collector.timer(8)**, **virtual-host-gatherer(1)**, **update-ca-certificates(8)**, **systemd(1)**.
