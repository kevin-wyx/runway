Runway
======

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

Start with `start.py`. Clean everything up with
`delete_all_runway_containers.py`. Because of the lvm commands, these
need to be run as root.

Project plans:
 - set up a VM that contains the containers (for easy distribution)
 - refactor to use many containers instead of an all-in-one container
 - allow the host to be something other than Ubuntu 16.04
 - allow the guest containers to be something other than Ubuntu

Use `bin/setup_guest_workspace.py` together with a manifest file (read
`README_MANIFEST.md` for further details) to get your components or manually
clone the appropriate code repos into `guest_workspaces\<your-workspace-name>`
directory by hand. Your workspace directory will be shared with your container.
This allows for easily having different versions of the source running
at the same time in different guest containers.

----

Getting code from your machine onto the running container

`runway_sync <runway host> [target container name]` syncs the pwd to
the host machine and the given target container. If the target
container name isn't given, it defaults to the special value "RECENT"
which syncs to the most recent container. The special value "NEW" will
start a new container with that code.
