# scc-hypervisor-collector Security Fundamentals

The `scc-hypervisor-collector` tool requires the use of sensitive
information, such as SUSE Customer Center (SCC) organisation, 
hypervisor login credentials, or access to SSH private keys, to
be able to collect the relevant details from hypervisor backends
specified in it's configuration and upload them to the SCC.

## Non-root user requirement

As the tool is intended to run without any special privileges it
will fail if it detects that it is running as the `root` user.

## Configuration settings

The `scc-hypervisor-collector` imposes the following restriction on
configuration settings:

* configuration files and directories must be owned by, and accessible
  only to, the user running the tool

This applies to all configuration files, whether specified directly via
the `--config` option, or found under the `--config-dir` directory,
which defaults to `~/.config/scc-hypervisor-collector`.

## Passwordless SSH Keys

The SSH tools themselves impose restrictions on the access permissions
and ownership of SSH private keys, similar to those that are specified
above for the `scc-hypervisor-collector`; failure to follow those
recommendations will lead to errors when attempting to leverage the
`qemu+ssh` protocol in Libvirt connection URIs.

## Log Messages and Files

The `scc-hypervisor-collector` depends upon external libraries to
collect the hypervisor details. As such it is possible that some of
those dependencies may contain code that could leak sensitive data
under certain failure scenarios. Similarly, a bug in the tool itself
could result in similar leakage.

Therefore, to mitigate the risk of exposing any sensitive data in
log messages, the log file (default `~/scc-hypervisor-collect.log`)
must be owned by, and only accessible to, the user running the tool.

Note that care has been taken to avoid leaking sensitive data via log
messages or to the standard output; when loaded configuration data is
rendered for display, sensitive values will be replaced by `********`.

Similarly our CI unit tests include checking for leaks of these
sensitive data fields during simulated success and failure scenaios.

## Hypervisor Credentials and SSH Keys

It is strongly recommended that any hypervisor access credentials,
or passwordless SSH keys, be associated with minimally privileged
accounts that can only be used to retrieve the relevant details.

This will help further mitigate any risks that may be associated
with inadvertently exposed credentials.