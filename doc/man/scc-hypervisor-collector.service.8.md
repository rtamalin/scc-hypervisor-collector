---
title: scc-hypervisor-collector.service
section: 8
header: scc-hypervisor-collector systemd integration
date: June 2022
---
# NAME

**scc-hypervisor-collector.service**, **scc-hypervisor-collector.timer** - **systemd(1)** integration for **scc-hypervisor-collector(1)**

# SYNOPSIS

scc-hypervisor-collector.service  
scc-hypervisor-collector.timer

# DESCRIPTION

The **scc-hypervisor-collector.service** **systemd(1)** unit will
run the **scc-hypervisor-collector(1)** command as the **scchvc**
user when triggered, if a valid configuration has been specified
in the **/var/lib/scchvc/.config/scc-hypervisor-collector**.

The **scc-hypervisor-collector.timer** **systemd(1)** unit will
trigger the **scc-hypervisor-collector.service** on a daily basis,
randomly skewed by up to 15 minutes.

# CONFIGURATION

To take advantage of the **scc-hypervisor-collector.service**, a
valid set of configuration settings must be created under the
**/var/lib/scchvc/.config/scc-hypervisor-collector** directory,
as documented in **scc-hypervisor-collector(5)**.

Run **scc-hypervisor-collector --check** as the **scchvc** user
to validate that the settings are correct.

## TLS/SSL CERTIFICATES

The **virtual-host-gatherer(1)** framework doesn't currently
permit the specification of certs that can be used to validate
connections to the specified hypervisors.

As such any certs that may be needed to securely connect to the
specified hypervisors will need to be registered with the system
certificate stores. See **update-ca-certificates(8)** for details.

# CUSTOMIZATION
The **systemctl edit** mechanism can be used to customize either of
the **scc-hypervisor-collector.service** and **scc-hypervisor-collector.timer**
units.

## CHANGING WHICH USER THE SERVICE RUNS AS

To change the user that the **scc-hypervisor-collector.service** runs
the **scc-hypervisor-collector(1)** command as from the **scchvc**
service account to **someuser** (with group membership **somegroup**),
create a drop-in snippet with the following content:

```
[Service]
User=someuser
Group=somegroup
```

## CHANGING WHEN THE TIMER TRIGGERS

To change the timer trigger from a daily cadence to a weekly cadence,
with a randomised skew of up to 6 hours rather than 15 minutes,
create a drop-in snippet with the following content:

```
[Timer]
OnCalendar=weekly
RandomizedDelaySec=6h
```

# AUTHORS

Originally developed by Fergal Mc Carthy (fmccarthy@suse.com) and Meera
Belur (mbelur@suse.com) for the SCC at SUSE LLC (scc-feedback@suse.de)


# LINKS

SUSE Customer Center: https://scc.suse.com

scc-hypervisor-collector on GitHub: https://github.com/SUSE/scc-hypervisor-collector

virtual-host-gatherer on GitHub: https://github.com/uyuni-project/virtual-host-gatherer

# SEE ALSO

**scc-hypervisor-collector(1)**, **scc-hypervisor-collector(5)**, **systemd(1)**
