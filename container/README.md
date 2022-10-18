Open Build Service Container Build
==================================

The `_service.example` can be used to setup a container build project that
will automatically retrieve the scc-hypervisor-collector source tarball
from GitHub and extract the Dockerfile and extrypoint.bash scripts. Run
`osc service manualrun` to set things up, and then `osc commit` to push
the container package build definition up to OBS so that it will start
attempting to build it.

You will also need to ensure that you have configured the OBS project in
which the container package is being built with 'Project Config' settings
that ensure it is building the container using the `docker` build type,
like this:

```
%if "%_repository" == "containers"
Type: docker
Repotype: none
Patterntype: none
%endif
```

Additionally you will need to define a `containers` repository that
points to the project in which the `scc-hypervisor-collector` is being
built, and then to the project associated with the SLE version that the
container will be based upon. For example the container build project
'Meta', when building a SLE 15 SP3 based container, could look something
like:

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
