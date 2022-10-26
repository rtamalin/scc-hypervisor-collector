Open Build Service Package Build
================================

The `_service.example` can be used to setup a *scc-hypervisor-collector*
package build that will automatically retrieve the *scc-hypervisor-collector*
source tarball from GitHub and extract the RPM spec file and systemd timer
and service unit files.

The spec file version value will also be updated to match the version just
pulled from Github.

If it doesn't already exist, touch the *scc-hypervisor-collector.changes*
file to ensure that change log entries are automatically generated for
upstream changes as part of the service run.

Run `osc service manualrun` to set things up, and then `osc addremove`
followed by `osc commit` to push the package build definition up to OBS
so that it will start attempting to build the package, which may fail if
the required dependencies are not available.

When updating an existing package you will need to manually delete the
existing source tarball, e.g. run `rm scc-hypervisor-collector*.tar.xz`,
before running the `osc service manualrun` to ensure that only the latest
tarball is stored in the OBS package definition.

The *scc-hypervisor-collector* package depends on having a viable version
of the *virtual-host-gatherer* package available to install; at the time
of writing this documenmt the existing OBS systemsmanagement:Uyuni:Master
package is based upon the 1.0.23 version tag, which doesn't include the
changes that were landed in PRs #27 and #29. Please ensure that you are
building a viable version of the *virtual-host-gatherer* package beside
the *scc-hypervisor-collector* package, and that it is enabled for use
when building other packages.
