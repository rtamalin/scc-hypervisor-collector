Open Build Service Container Build
==================================

The `_service.example` can be used to setup a container build project
that will automatically retrieve the scc-hypervisor-collector source
tarball from GitHub and extract the Dockerfile and extrypoint.bash
scripts.

The buildtime service definitions will ensure that the appropriate 
values are substituted for the placeholders during the package build.

Run `osc service manualrun` to setup the container build, then run
`osc addremove` to include the modified files in the changeset and
finally run `osc commit` to push the container build definition up
to OBS so that it will start attempting to build it, which will fail
until the required configuration steps, outlined below, are completed.

Additionally you will need to define a `containers` repository that
points to the project in which the `scc-hypervisor-collector` is being
built, and then to the project associated with the SLE version that the
container will be based upon.

For example the container build project 'Meta', if building a SLE 15 SP3
based container, should look something like:

```
<project name="home:someuser:systemsmanagement:containers">
  <title>SCC Hypervisor Collector Container Images</title>
  <description>Container Images containing the SCC Hypervisor Collector</description>
  <person userid="someuser" role="maintainer"/>
  <repository name="containers">
    <!-- specify the project repository from which to retrieve the
         scc-hypervisor-collector packages -->
    <path project="home:someuser:systemsmanagement" repository="SLE_15_SP3"/>
    <!-- specify the project repository from which to retrieve the SLE
         15 SP3 base packages, which will expand to contain all the
	 repository entries specifed for the images repo in that project -->
    <path project="SUSE:Templates:Images:SLE-15-SP3:Base" repository="images"/>
    <arch>x86_64</arch>
  </repository>
</project>
```

Finally, you will need to ensure that you have configured the OBS project in
which the container package is being built with 'Project Config' settings
that ensure it is building the container using the `docker` build type,
like this:

```
%if "%_repository" == "containers"
Type: docker
Repotype: none
Patterntype: none

# Required to resolve a dependency choice issue.
Prefer: dbus-1
%endif
```

NOTE: If you named your containers repository something other than `containers`,
e.g `SLE_15_SP3_containers`, then make sure that the repository name in your 
'Project Config' settings matches, otherwise the build will fail.
