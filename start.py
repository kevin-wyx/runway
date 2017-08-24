#!/usr/bin/env python3

import argparse
# import datetime
import os
import sys

from libs import colorprint
from libs import workspaces
from libs.cli import run_command
from libs.manifest import Manifest
import setup_and_run_ansible_on_guest

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
RUNWAY_DIR = SCRIPT_DIR
DEFAULT_BASE_IMAGE = "runway-base"
# Using colons makes using lxc-cli inconvenient, and using periods makes it
# an invalid hostname, so just use all dashes
# DEFAULT_CONTAINER_NAME = "swift-runway-{}".format(
#     datetime.datetime.now().strftime("%F-%H-%M-%S-%f"))
DEFAULT_DISTRO = "ubuntu"
DEFAULT_VOL_SIZE = "10G"


def exit_with_error(error_text):
    colorprint.error(error_text)
    sys.exit(1)


def get_manifest(workspace_name):
    if workspace_name is None:
        exit_with_error("No workspace found.")
    workspace_path = workspaces.get_workspace_path(workspace_name)
    manifest_path = workspaces.get_manifest_path(workspace_name)
    try:
        return Manifest(manifest_path, workspace_path)
    except Exception as e:
        exit_with_error(e.message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--debug', action='store_true',
                        default=False, help="Enable debug mode")
    parser.add_argument('-d', '--distro', default=DEFAULT_DISTRO,
                        help="Container distro. Default: "
                             "{}".format(DEFAULT_DISTRO))
    parser.add_argument('-i', '--base-image', default=DEFAULT_BASE_IMAGE,
                        help="Base image. Default: "
                             "{}".format(DEFAULT_BASE_IMAGE))
    parser.add_argument('-n', '--no-install', action='store_true',
                        default=False, help="Don't install any components.")
    parser.add_argument('-r', '--delete-container', action='store_true',
                        default=False, help="Delete container after snapshot.")
    parser.add_argument('-s', '--no-snapshot', action='store_true',
                        default=False, help="Don't create snapshot.")
    parser.add_argument('-v', '--vol-size', default=DEFAULT_VOL_SIZE,
                        help="Vol size. Default: {}".format(DEFAULT_VOL_SIZE))
    parser.add_argument('-w', '--workspace', default=None,
                        help="Workspace name. Default: last workspace with "
                             "name formatted like "
                             "'{}xxx'".format(workspaces.WORKSPACE_PREFIX))

    args = parser.parse_args()
    debug = args.debug
    debug_string = " --debug" if debug else ""
    distro = args.distro
    base_image = args.base_image
    install_components = not args.no_install
    install_string = "" if install_components else " --no-install"
    delete_container = args.delete_container
    delete_container_string = "" if not delete_container \
        else " --delete-container"
    no_snapshot = args.no_snapshot
    vol_size = args.vol_size
    workspace_name = args.workspace

    if os.geteuid() != 0:
        exit_with_error("This script must be run as root.")

    if workspace_name is None:
        workspace_name = workspaces.get_last_workspace_name()
    manifest = get_manifest(workspace_name)
    family = manifest.get_config_option("family")
    if family is not None:
        if base_image != DEFAULT_BASE_IMAGE:
            colorprint.warning("You provided a base image name, but a family "
                               "name is specified in the manifest. Your base "
                               "image name will not be used.")
        base_image = family

    container_name = workspace_name

    vol_count = int(manifest.runway_options.get('number_of_drives', 8))

    try:
        run_command("./make_base_container.sh "
                    "{} {} {} {}{}".format(distro, container_name, base_image,
                                           vol_size, debug_string), RUNWAY_DIR)
        setup_and_run_ansible_on_guest.setup_and_run_ansible(
            container_name, debug=debug, drive_count=vol_count)
        # If we're in a "no install" mode, skip the rest
        # we assume it's already all set up (ie started from a snapshot)
        if install_components:
            # Now find code repos in the guest and install them.
            # At this point, all the code is on the guest in
            # `/home/swift/code/`.
            # We need to find repos there (excluding stuff like swift itself)
            # and call the install command from the manifest or install.sh at
            # the root of the component (not finding any of them is ok).
            run_command("./generic_installer.py {}".format(container_name),
                        RUNWAY_DIR)
            if not no_snapshot:
                run_command("./snapshot_created_container.sh "
                            "{} {}{}{}".format(container_name, base_image,
                                               debug_string,
                                               delete_container_string),
                            RUNWAY_DIR)
    except Exception as e:
        exit_with_error(str(e))

    colorprint.success("Container '{}' successfully "
                       "created.\n".format(container_name))
