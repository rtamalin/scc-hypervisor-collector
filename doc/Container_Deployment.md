# Container based deployment

The provided [Dockerfile](../container/Dockerfile) can be used to
build a SUSE Linux Enterprise 15 based container image, leveraging
[entrypoint.bash](../container/entrypoint.bash) script as the entry
point to ensure that the container runtime environment is set up
correctly before running the `scc-hypervisor-collector` tool.

## Bind Mount Volumes

The container expects that a properly setup directory will be bind
mounted on `/var/lib/scchvc`.

This directory should contain the following:

* a `.config/scc-hypervisor-collector` sub-directory, with desired
  configuration settings.
* optionally a `.ssh` sub-directory with relevant SSH private key
  supporting passwordless access to any `qemu+ssh` protocol based
  Libvirt connection URIs specified in the configuration settings.
* optionally a `certs` directory containing any certs that are
  needed to access any HTTPS protocol based hypervisor connection
  URLs.

This directory, and all of the sub-directories and contained files,
should be owned by, and accessible only to, the same non-root user,
per the `scc-hypervisor-collector` [Security Recommendations](Security.md).

## Entrypoint

The [entrypoint.bash](../container/entrypoint.bash) script expects
to find a host directory bind mounted to `/var/lib/scchvc` that is
owned by, and accessible only to an appropriate non-root user.

The script will perform the following actions:

* determine the user and group ids associated with the `/var/lib/scchvc`
  and dynamically create a local `scchvc` user and associated `scchvc`
  group with the same user and group ids within the container runtime,
  whose home directory is `/var/lib/scchvc`.
* if any certs have been provided in the `/var/lib/scchvc/certs` directory
  they will be copied to the `/etc/pki/trust/anchors` directory within
  the container runtime, and `update-ca-certificates` will be run to
  ensure that they are available for HTTPS protocol connection verification.
* run the `scc-hypervisor-collector` as the dynamically created `scchvc`
  user, using specified, or default if not provided, container run
  arguments.

# Building the container

Currently the [Dockerfile](../container/Dockerfile) is intended to be
leveraged as part of an [Open Build Service](https://build.opensuse.org)
SLE 15 SP3 based container build.

# Container based workflow

The image built by the [Dockerfile](../container/Dockerfile), leveraging
the provided [entrypoint.bash](../container/entrypoint.bash), is intended
to be run against a directory that has been setup appropriately to act as
the home directory of a user that will run the `scc-hypervisor-collector`
command, as defined above.

This directory should be bind mounted to the `/var/lib/scchvc` directory
when running the tool via a container.

Built containers have been tested successfully using `podman` and `docker`.

## Example container run

Using `/home/someuser`, which has been setup appropriately with the
necessary configuration settings, appropriate certs and SSH private
keys, and the built container, the `scc-hypervisor-collector` check
mode can be run via the container using the following command (replace
`podman` with `docker` if needed):

```
% sudo podman run --rm \
    -v /home/someuser:/var/lib/scchvc \
    ${CONTAINER_IMAGE_REGISTRY_URL} \
    --check
```

If the configuration check passes you can run the tool against the
configuration using:

```
% sudo podman run --rm \
    -v /home/someuser:/var/lib/scchvc \
    ${CONTAINER_IMAGE_REGISTRY_URL}
```
