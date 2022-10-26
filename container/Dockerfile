# Define the names/tags of the container
# NOTE: First tag used to derive build name if not specified
#!BuildTag: suse/scc-hypervisor-collector/sle%OS_VERSION_ID_SP%:%PKG_VERSION%.%TAG_OFFSET% suse/scc-hypervisor-collector/sle%OS_VERSION_ID_SP%:%PKG_VERSION%.%TAG_OFFSET%.%RELEASE% suse/scc-hypervisor-collector/sle%OS_VERSION_ID_SP%:%PKG_VERSION% suse/scc-hypervisor-collector/sle%OS_VERSION_ID_SP%:latest

# Ensure this base container image version matches the images repository version
FROM suse/sle15:15.3

# Define labels according to https://en.opensuse.org/Building_derived_containers
# labelprefix=com.suse.example
PREFIXEDLABEL org.opencontainers.image.title="SCC Hypervisor Collector SLE %OS_VERSION_NO_DASH% container"
PREFIXEDLABEL org.opencontainers.image.description="This contains scc-hypervisor-collector %PKG_VERSION%"
PREFIXEDLABEL org.opensuse.reference="registry.suse.com/suse/scc-hypervisor-collector:%PKG_VERSION%.%RELEASE%"
PREFIXEDLABEL org.openbuildservice.disturl="%DISTURL%"
PREFIXEDLABEL org.opencontainers.image.created="%BUILDTIME%"

# Put additional files into container
COPY entrypoint.bash /root/
RUN chmod 700 /root/entrypoint.bash

# Workaround for https://github.com/openSUSE/obs-build/issues/487
RUN zypper --non-interactive in sles-release

# Install further packages using zypper
RUN zypper install -y scc-hypervisor-collector-common

# This command will get executed on container start by default
ENTRYPOINT ["/root/entrypoint.bash"]
CMD ["--config_dir", "/var/lib/scchvc/.config/scc-hypervisor-collector"]
