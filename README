A project to help you take flight with a storage system (get it?).

This sets up a swift-all-in-one (SAIO) dev environment in an lxc container.
Eventially it will also include projects like swift3, metadata searching,
and filesystem access.

This project has three target use cases:
 - Developers looking to contribute code to any of the constituent projects
 - Developers looking for an API test target against which to write apps
 - Something easily consumable for CI to integrate into a QA process

Requires a lvm volume group named "swift-runway-vg01", LXD version 2.14 or
higher and assumes it's running on an Ubuntu 16.04 host.

Start with `start.sh`. Clean everything up with
`delete_all_runway_containers.py`. Because of the lvm commands, these
need to be run as root.

Project plans:
 - set up a VM that contains the containers (for easy distribution)
 - refactor to use many containers instead of an all-in-one container
 - allow the host to be something other than Ubuntu 16.04
 - allow the guest containers to be something other than Ubuntu

Clone the appropriate code repos into the `components` directory.

The `components` directory is where the source repos for the
constituent parts go. This is what's installed on the guest
containers. However, it's not directly installed from there. It's
first copied into a unique directory in the `guest_workspaces`
directory, and those are in turn bind-mounted to the guest container.
This allows for easily having different versions of the source running
at the same time in different guest containers.

----

Getting code from your machine onto the running container

`runway_sync <runway host> [target container name]` syncs the pwd to
the host machine and the given target container. If the target
container name isn't given, it defaults to the special value "RECENT"
which syncs to the most recent container. The special value "NEW" will
start a new container with that code.
