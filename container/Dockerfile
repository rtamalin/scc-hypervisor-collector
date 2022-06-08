#!BuildTag: suse/scc-hypervisor-collector:15.3
FROM suse/sle15:15.3

#USER wwwrun
#WORKDIR /srv/www

# Put additional files into container
COPY entrypoint.bash /root/
RUN chmod 700 /root/entrypoint.bash

# Work around https://github.com/openSUSE/obs-build/issues/487
RUN zypper install -y sles-release

# Install further packages using zypper
RUN zypper install -y scc-hypervisor-collector-common

# This command will get executed on container start by default
ENTRYPOINT ["/root/entrypoint.bash"]
CMD ["--config_dir", "/var/lib/scchvc/.config/scc-hypervisor-collector"]
