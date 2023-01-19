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

The **scc-hypervisor-collector(1)** collects details relevant to
subscription compliance tracking from customer hypervisor solutions
and uploads them to the SUSE Customer Center (SCC), using provided
customer credentials.

# COLLECTED DETAILS

For each hypervisor node that is managed by the specified hypervisors,
the following details are collected:

**Hypervisor Node Name**
: The name assigned to the hypervisor node

**Hypervisor Node ID**
: The id assigned to the hypervisor node

**Hypervisor Type**
: The id assigned to the hypervisor node

**RAM**
: Total system memory

**CPU Architecture**
: The type of CPU, e.g. **x86_64**, **aarch64**

**CPU Topology**
: The number of sockets, cores and threads

**Hosted VMs**
: List of hosted VM with identification and state info.

For each hosted VM the following details are collected:

**Name**
: The hypervisor configuration name for to the VM

**UUID**
: The UUID associated with the VM if has been registered with the SCC.
  In some cases (VMWare, see below) it may be a mangled form of the
  origial UUID assigned by the hypervisor node.

**VMWare UUID** (VMWare Hypervisors only)
: The UUID that VMWare assigned to the VM.
  Depending on the VMWare hypervisor host software version, the VM
  BIOS version used, and the Linux distribution/release being run,
  in some cases the system UUID reported within the running instance
  may reverse the byte order within each of the first 3 elements of
  the UUID.

**VM State**
: The state of the VM, i.e. running or stopped/shutoff.

## EXAMPLES OF COLLECTED DETAILS

The following examples are YAML representations of the details that
are collected from a QEMU/KVM Libvirt host and a VMWare vCenter:

```
[libvirt1]
kvmhost1.example.com:
  capabilities:
    cpu_topology:
      arch: x86_64
      cores: 8
      sockets: 2
      threads: 1
    ram_mb: 128781
    type: QEMU
  id: af78bfa8-67df-4d84-8d32-e40eb2404ac1
  name: sle15-dev
  vms:
    some-workload-vm-1:
      uuid: c44bae94-bab0-44f5-8603-0d770344facc
      vmState: running
    some-workload-vm-2:
      uuid: f5319c28-377f-46fe-acee-5509a356f652
      vmState: running
    some-workload-vm-3:
      uuid: 51b62ad3-effd-45db-b508-1ac47a528b93
      vmState: running
    some-workload-vm-4:
      uuid: cf46f104-5806-4ddd-9e99-32d167d063a3
      vmState: running

[vcenter1]
esx1.dc1-vcenter.example.com:
  capabilities:
    cpu_topology:
      arch: x86_64
      cores: 12
      sockets: 2
      threads: 24
    ram_mb: 253917
    type: vmware
  id: '''vim.HostSystem:host-15'''
  name: esx1.dc1-vcenter.example.com
  vms:
    some-workload-vm-1:
      uuid: 422270db-f382-4955-8cbd-75736a64089b
      vmState: running
      vmware_uuid: 422270db-f382-4955-8cbd-75736a64089b
    another-workload-vm-2:
      uuid: 4222dec1-6226-4f44-95e4-05156ea0f4b5
      vmState: running
      vmware_uuid: 4222dec1-6226-4f44-95e4-05156ea0f4b5
esx2.dc1-vcenter.example.com:
  capabilities:
    cpu_topology:
      arch: x86_64
      cores: 12
      sockets: 2
      threads: 24
    ram_mb: 262109
    type: vmware
  id: '''vim.HostSystem:host-27'''
  name: esx2.dc1-vcenter.example.com
  vms:
    another-workload-vm-1:
      uuid: 42225602-4139-44fb-b111-e5b8df028b1c
      vmState: running
      vmware_uuid: 42225602-4139-44fb-b111-e5b8df028b1c
    linux-workload-vm-3:
      uuid: 5dec2242-969f-1dee-8137-209da409ec2b
      vmState: running
      vmware_uuid: 4222ec5d-9f96-ee1d-8137-209da409ec2b
    linux-workload-vm-1:
      uuid: 564d2049-beb3-8f38-bfea-488d2a4186cd
      vmState: running
      vmware_uuid: 564d2049-beb3-8f38-bfea-488d2a4186cd
    linux-workload-vm-2:
      uuid: 7e0f2242-f1c3-dd4a-b902-18f602165074
      vmState: running
      vmware_uuid: 42220f7e-c3f1-4add-b902-18f602165074
```

# OPTIONS

  **-h**, **--help**
  : Provides basic details about the available command line options.

  **-V**, **--version**
  : Reports the version of **scc-hypervisor-collector**.

  **-q**, **--quiet**
  : Runs in quiet mode, only reporting errors.

  **-v**, **--verbose**
  : Runs in verbose mode, reporting additional details.

  **-c**, **--config <CONFIG_FILE>**
  : Specifies a file containing YAML configuration settings. If both
    **--config** and **-config-dir** options are specified, the
    specified **--config** file contents will be merged over the
    settings loaded from the **-config-dir** directory, superceding
    any existing settings.

  **--config-dir**, **--config_dir <CONFIG_DIR>**
  : Specifies a directory containing one of more YAML configuration
    files, with **.yaml** or **.yml** suffixes that will be merged
    together, in lexical sort order, to construct the configuration
    settings. Note that sub-directories will not be traversed.
    Defaults to **~/.config/scc-hypervisor-collector**.

  **-C**, **--check**
  : Checks the specified configuration settings for correctness, reporting
    any issues found.

  **-S**, **--scc-credentials-check**
  : Validates that the supplied SCC credentials can be used to connect
    to the SCC.

  **-L**, **--logfile <LOG_FILE>**
  : Specifies the path to the log file in which to write log messages.
    Defaults to **~/scc-hypervisor-collector.log**.

  **-u**, **--upload**
  : Specifies whether to upload the collected results to the SCC.

  **-r**, **--retry_on_rate_limit**
  : Specifies whether to retry uploading to SCC when rate limit is hit.
    If the **scc-hypervisor-collector** is being run frequently, e.g.
    daily, then it may be preferable to just wait until the next run,
    rather than delaying and retrying again after the SCC rate limit
    response's retry delay.

  **-i**, **--input <INPUT_FILE>**
  : Specifies the path to a YAML file containing previously collected
    results. If this option is specified then any hypervisor backends
    configuration will be ignored and the contents of this file, so
    long as they conform to the expected results layout, will be used
    as the collected results to be uploaded. This option cannot be used
    in conjunction with the **-o**/**--output** option.

  **-o**, **--output <OUTPUT_FILE>**
  : Specifies the path to a file to which the YAML formatted results
    of the details collected from the specified hypervisor backends
    will be written. Any existing file contents will be lost, and the
    file mode settings will be modified so that only ownwer can access
    it. This option also disables uploading results to the SCC, and
    cannot be used in conjunction with the **-i**/**--input** option.

# SECURITY CONSIDERATIONS

The **scc-hypervisor-collector(1)** is intended to be run from a
restricted service account with no special privileges, and will
exit immediately if it detects that it is running with superuser
privileges.

## HYPERVISOR ACCESS CREDENTIALS

Any hypervisor access credentials that are provided for use with
the **scc-hypervisor-collector(1)** should have minimal privileges
sufficent to allow retrieving the required details about the
hypervisor nodes and then VMs running on them.

## CONFIGURATION SETTINGS & LOG FILE PERMISSIONS

As the **scc-hypervisor-collector(5)** configuration settings
will contain sensitive information such as passwords, the command
requires that all specified configuration files and directories
must be owned by the non-root user that is running the command,
with restrictive permissions allowing only that user to access
those files.

Similarly, while every effort has been taken to ensure that no
sensitive data is being written to the log files, to limit
potential exposure of such information the log files must also
be owned by, and only accessible by, the user that is running
the **scc-hypervisor-collector(5)** command.

## TLS/SSL CERTIFICATES

The **virtual-host-gatherer(1)** framework only supports certs
that are registered with the system certificate stores.
See **update-ca-certificates(8)** for details.

## SSH KEYS

For any **Libvirt** hypervisors that are specified with a **qemu+ssh**
type URI, appropriate SSH keys that support passwordless SSH access
to the target hypervisor node, must be available in the **~/.ssh/**
directory.

See **ssh-keygen(1)** for more details on how to generate appropriate
SSH keys if needed, and **ssh(1)** for the appropriate permissions
for the **~/.ssh/** directory and any keys stored there.

## SEPARATE COLLECTION AND UPLOAD RUNS

Leveraging the **-o**/**--output** and **-i**/**--input** options, it
will be possible to run the details collection stage only, saving the
collected results to a file, which can then be uploaded to the SCC in
a separate run, potentially on a different system.

This allows for customer deployment scenarioes where the system that
has access to be able to collect details from the hypervisor backends
may not have internet access to be able to upload the collected details
to the SCC; the details collection can phase can be run on an internal
system with the necessary access, with the saved collection results
then being transferred to another system with internet access that can
run the upload phase.

### Reviewing and sanitizing the collected results

This separation of the collection and upload phases also allows the
collected results data to be reviewed and potentially sanitised, e.g.
hostnames and VM names can be changed.

However, certain values, such as the VM UUIDs and Libvirt host system
properties and identifiers should not modified as these values are used
to cross reference collection details with any associated subscriptions
in the SCC.

# CONFIGURATION SETTINGS

Configuration settings are specified in YAML format and must contain:

**backends**
: a list of hypervisor backends from which to retrieve relevant
  details

**credentials**
: a collection of credentials that will be used to upload the
  collected details to the SUSE Customer Center.

See **scc-hypervisor-collector(5)** for details about the possible
configuration settings.

## CONFIGURATION MANAGEMENT

The configuration settings, which must be in YAML format, can be
specified as:

* a single config file via the **--config** option.
* a directory containing a set of YAML files (with **.yaml** or
  **.yml** suffixes) via the **-config-dir** option.

If a configuration directory is specified then any YAML files found
under that directory, not traversing sub-directories, with **.yaml**
or **.yml** suffixes, will be processed in lexical sort order,
merging their contents together.

If a configuration file was specified, it's contents will be processed
last and merged over any existing configuration settings.

This scheme allows for configuration settings to be split up into
multiple files, e.g. credentials can be specified in one file,
and the hypervisor backends in one or more files. Additionally
specific config settings can be overriden by an explicitly
specified config file.

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

**0**
:  Run completed successfully, or configuration settings
      are valid if check mode (**--check**) was specified.

**1**
:  An error occurred.

# IMPLEMENTATION

**scc-hypervisor-collector(1)** is implemented in Python.
It communicates with the SUSE Customer Center via a RESTful
JSON API over HTTP using TLS encryption.

## HYPERVISOR DETAILS RETRIEVAL

The **gatherer** Python module provided by the **virtual-host-gatherer(1)**
command is used to retrieve the details from the configured hypervisors.

# ENVIRONMENT

**scc-hypervisor-collector(1)** respects the HTTP_PROXY environment
variable.  See https://www.suse.com/support/kb/doc/?id=000017441 for
more details on how to manually configure proxy usage.

# FILES AND DIRECTORIES

**~/.config/scc-hypervisor-collector/**
: Default configuration directory containing YAML configuration files,
  merged together in lexical sort order. Directory and files must be
  owned by, and only accessible by, the user running the
  **scc-hypervisor-collector(5)** command.

**~/scc-hypervisor-collector.log**
: Default log file which will be automatically rotated and compressed
  if it gets too large. Log files must be owned by, and only accessible
  by, the user running the **scc-hypervisor-collector(5)** command.
  Will be created with appropriate permissions if no log file exists.

**~/.ssh/** (optional)
: Directory holding any SSH keys (**ssh-keygen**) needed to access
  **Libvirt** with **qemu+ssh** URIs.

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
