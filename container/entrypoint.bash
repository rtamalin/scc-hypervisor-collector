#!/bin/bash -eu

export PATH=/usr/bin:/bin:/usr/sbin:/sbin

# scc-hypervisor-collector configuration should be available under
# /var/lib/scchvc, so we need to ensure that we have a user defined
# in our container environment that matches the user id of that mount
# point.

shcuser=scchvc
name=scc-hypervisor-collector
_localstatedir=/var
_svcdir=${_localstatedir}/lib/${shcuser}

update-ca-certificates

if [[ ! -d ${_svcdir} ]]; then
    echo "Error: no ${_svcdir} directory found; did you bind mount the service account dir to ${_svcdir}?"
    exit 1
fi

uid_gid=(
    $(stat -c '%u %g' ${_svcdir})
)

# ensure that the required group exists or add it with matching gid
# if needed
getent group ${shcuser} >/dev/null || groupadd \
    -r \
    -g ${uid_gid[1]} \
    ${shcuser}

# ensure that the required user exists or add it with matching udi
# if needed
getent passwd ${shcuser} >/dev/null || useradd \
    -r \
    -g ${shcuser} \
    -u ${uid_gid[0]} \
    -d ${_svcdir} \
    -s /sbin/nologin \
    -c "user for ${name}" ${shcuser}

cmd_args=(
    ${name}
    "${@}"
)

set -vx
su - ${shcuser} --shell /bin/bash -c "${cmd_args[*]}"
