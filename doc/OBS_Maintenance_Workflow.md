OBS Maintenance Workflow
========================

# `scc-hypervisor-collector` package

The `scc-hypervisor-collector` package is built in the Open Build Service
(OBS) under the [systemsmanagement:SCC](https://build.opensuse.org/project/show/systemsmanagement:SCC)
project.

While an `_service` file is used to manage the retrieval of the sources,
and the subsequent extraction of the [spec file](../scc-hypervisor-collector.spec)
and [systemd unit scripts](../systemd), and update the changes file with
details about the PRs landed since between the most recent tag and last
update, as well as setting the spec file version appropriately, these
actions currently need to be triggered manually.

The recommended command sequence to use is as follows, replacing the
placeholder OBS user account (`obsuser`) with your OBS user name:

* Branch checkout the systemsmanagement:SCC/scc-hypervisor-collector package

```
% osc bco systemsmanagement:SCC scc-hypervisor-collector
```

* Switch to the branched checkout directory and update the sources
  and packages changes file, extract the spec file and system unit
  files:

```
% cd home:obsuser:branches:systemsmanagement:SCC/scc-hypervisor-collector
% rm *.tar.xz  # remove the existing versioned sources tarball
% osc service manualrun  # downloads new sources tarball, extracts file
% osc addremove  # Adds new files, removes deleted ones
% osc commit
```

* Verify that the updated package builds, resolving any issues encountered.

* Submit the working package build to the main project:

```
% osc submitrequest
```

* Wait for a `systemsmanagement:SCC` project maintainer to review your
  request and hopefully accept it.


# `scc-hypervisor-collector` container

The `scc-hypervisor-collector` container image is built in the Open Build
Service under the [systemsmanagement:SCC:containers](https://build.opensuse.org/project/show/systemsmanagement:SCC:containers)
project.

Similarly to the `scc-hypervisor-collector` package, an `_service`
file is used to manage to retrieval of the sources, and the subsequent
extraction of the [Dockerfile](../container/Dockerfile) and the
[extrypoint.bash](../container/extrypoint.bash) scripts, though again
these actions currently need to be triggered manually.

The recommended command sequence to use is as follows, replacing the
placeholder OBS user account (`obsuser`) with your OBS user name,
and assuming you are updating the SLE 15 SP3 based container:

* Branch checkout the systemsmanagement:SCC:containers/scc-hypervisor-collector-sle15sp3
  container package

```
% osc bco systemsmanagement:SCC:containers scc-hypervisor-collector-sle15sp3
```

* Switch to the branched checkout directory and update the sources,
  and extracting the `Dockerfile` and `extrypoint.bash` scripts:

```
% cd home:obsuser:branches:systemsmanagement:SCC:containers/scc-hypervisor-collector-sle15sp3
% rm *.tar.xz  # remove the existing versioned sources tarball
% osc service manualrun  # downloads new sources tarball, extracts file
% osc addremove  # Adds new files, removes deleted ones
% osc commit
```

* Verify that the updated package builds, resolving any issues encountered.

* Submit the working package build to the main project:

```
% osc submitrequest
```

* Wait for a `systemsmanagement:SCC:containers` project maintainer to review
  your request and hopefully accept it.

