# Adhoc Testing

The `bin/gen_large_datasets` utility can be utilised to generate synthesised:

  * "collected" results for simulated VMWare and/or Libvirt hypervisor
    topologiies.

  * systems details including hostnames, system UUIDs, tokens and
    created\_at time stamps for the relevant nodes in the simulated
    hypervisor topologiies.

The `bin/bulk_create` utility can be used to create the fictitious systems
in the simulated hypervisor topologies.

The synthesised results can be passed as then collection details source to
the `scc-hypervior-collector` command, via then --input option, alllowing
validation that uploading hypervisor topology details to the SCC works
correctly using the new `/connect/organization/virtualization_hosts` PUT
request.


## `gen_large_datasets`

NOTE: This command should be run in an environment where the `scc_hypervisor_collector.api` can be imported.

```
usage: gen_large_datasets [-h] [-o OUTPUT] [-s SYSTEMS] [-S SUFFIX] [-V VMWARE] [-E ESX_HOSTS] [-e ESX_VMS] [-L LIBVIRT]
                          [-l LIBVIRT_VMS]

Generate data sets for SCC VirtualizationHosts API testing

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        The output file where the generated data set will be written. (Default: /tmp/test_collected_results.yaml)
  -s SYSTEMS, --systems SYSTEMS
                        The output file where details of generated Libvirt and VM systems for use with bulk creation will be written.
                        (Default: /tmp/test_linux_systems.yaml)
  -S SUFFIX, --suffix SUFFIX
                        An optional suffix that will be added to the hostnames of generated system names.
  -V VMWARE, --vmware VMWARE
                        The number of VMWare backends to add to the data set. (Default: 0)
  -E ESX_HOSTS, --esx-hosts ESX_HOSTS
                        The number of ESX hosts per VMWare backend. (Default: 2)
  -e ESX_VMS, --esx-vms ESX_VMS
                        The number of VMs per ESX host in each VMWare backend. (Default: 10)
  -L LIBVIRT, --libvirt LIBVIRT
                        The number of Libvirt backends to add to the data set. (Default: 0)
  -l LIBVIRT_VMS, --libvirt-vms LIBVIRT_VMS
                        The number of Libvirt backends to add to the data set. (Default: 10)
```


The `gen_large_datasets` tool takes as arguments simulation parameters
specifying:

  * the number of VMWare vCenters, associated ESX hosts, and number of SLE
    VMs per ESX host.

  * the number of SLE Libvirt hosts, and number of SLE VMs per Libvirt host.

  * an optional suffix that will be included in all names where appropriate.

The default generated files, which can be overridden via the appropriate
options, are:

  * `/tmp/test_collected_results.yaml` for simulated collected results.

  * `/tmp/test_linux_systems.yaml` for simulated systems details.

For example to generate a simulated collected results, and associated systems
details for a mixture of 2 vCenters, each with 10 ESX hosts running 50 SLE VMs,
and 20 Libvirt hosts each running 50 SLE VMs, you could use a command like the
following:

```
$ .tox/dev/bin/python3 bin/gen_large_datasets -V 2 -E 5 -e 100 -L 20 -l 50 -S mixed2k
```


## `bulk_create`

```
usage: bulk_create [-h] [--systems_per_request SYSTEMS_PER_REQUEST] [--rmt_uuid RMT_UUID] [--rmt_name RMT_NAME] [-a API_BASE_URL]
                   [-u USERNAME] [-p PASSWORD] [-s SYSTEMS] [-c]

Bulk create systems SCC VirtualizationHosts API testing

optional arguments:
  -h, --help            show this help message and exit
  --systems_per_request SYSTEMS_PER_REQUEST
                        The max number of systems to upload per request to the SCC. (Default: 200)
  --rmt_uuid RMT_UUID   The RMT UUID to report to the SCC. (Default: ecf431f8-7faa-48a4-a3f1-6d3abb199086)
  --rmt_name RMT_NAME   The RMT name to report to the SCC. (Default: rmt.test.example.com)
  -a API_BASE_URL, --api_base_url API_BASE_URL
                        The SCC API base URL. (Default: http://localhost:3000)
  -u USERNAME, --username USERNAME
                        The SCC mirroring credentials username to use for bulk creation. Can be specified via SCC_USERNAME env var.
  -p PASSWORD, --password PASSWORD
                        The SCC mirroring credentials password to use for bulk creation. Can be specified via SCC_PASSWORD env var.
  -s SYSTEMS, --systems SYSTEMS
                        The input file containing the details of the Libvirt host and VM systems to bulk create. (Default:
                        /tmp/test_linux_systems.yaml)
  -c, --check_creds     Verify that the supplied SCC mirroring credentials are valid.
```

The `bulk_create` tool takes as arguments:

  * the SCC credentials to use to upload the simulated systems, which can be
    alternatively specified via the SCC_USERNAME and SCC_PASSWORD environment
    variables.

  * the SCC API URL to use.

  * the simulated systems details file generated by the `gen_large_datasets`
    tool.

  * optional simulated RMT identification details.

  * optional number of systems to upload per request

The specified SCC credentials can be validated using the `--check_creds`
option as well.

For example to create the simulated systems associated with the above
generated `mixed2k` dataset in a SCC development environment running on
localhost:5000, you could use a command like the following:

```
$ bin/bulk_create -s /tmp/test_linux_systems.yaml -a http://localhost:5000 -u ${SCC_ACCOUNT} -p ${SCC_PASSWORD}
```

## Testing SCC VirtualizationHosts API

You can use the `bin/gen_large_datasets` tool (above) to create the synthesised collected results and associated systems details.

Once you have registered the systems using `bin/bulk_create` tool (above) you can now run the `scc-hypervisor-collector` command to upload the synthesised collected results, using the configured SCC credentials, as follows:

```
$ bin/scc-hypervisor-collector --upload --input /tmp/test_collected_results.yaml
```

## Cleaning up the fake systems created with `bulk_create`

Once testing has finished you can easily delete all of the fake systems that were registered via the SCC Web UI as follows:

* Log in to the SCC account associated with the Organization that the systems were registered to.

* Select the appropriate organization from the "My Organizations" list

* Select the "Proxies" tab

* Locate the "fake" RMT with the specified UUID (default per the help message for the `bulk_create` tool) and click on the "Show details" link

* Click on the "Delete this registration proxy" button to delete the fake RMT and all associated systems registered via it.
