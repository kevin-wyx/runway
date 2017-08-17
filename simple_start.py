#!/usr/bin/env python3

# simple start for setting up a new workspace and starting a guest
# All options come from the manifest; there are no options for this tool

import sys
import os
from shutil import copyfile

from libs.manifest import Manifest
from libs import workspaces
from libs import colorprint
from libs.cli import run_command
import setup_and_run_ansible_on_guest

if __name__ == '__main__':
    usage = '%s manifest_file' % sys.argv[0]

    try:
        manifest_path = os.path.abspath(sys.argv[1])
    except IndexError:
        print('Usage: %s' % usage)
        sys.exit(1)


    RUNWAY_DIR = os.path.abspath(os.path.dirname(__file__))

    # need to parse the manifest file first to get the runway options (family)
    man = Manifest(manifest_path, None)

    # create workspace dir from runway_options['family']
    workspaces.WORKSPACE_PREFIX += '%s-' % man.runway_options['family']
    workspace_name = workspaces.get_new_workspace_name()
    workspace_path = workspaces.create_workspace_dir(workspace_name)
    man.workspace_dir = workspace_path

    # get manifest components into workspace
    man.retrieve_components()

    # get a copy fo the manifest into the workspace directory
    copyfile(manifest_path, os.path.join(workspace_path, 'manifest.cfg'))

    # make guest etc etc
    container_name = workspace_name

    try:
        vol_size = man.runway_options['drive_size']
        base_image = 'runway-base-%s' % man.runway_options['family']
        debug = man.runway_options.get('debug') == 'True'
        debug_string = " --debug" if debug else ""
        vol_count = int(man.runway_options['number_of_drives'])
        distro = man.runway_options.get('distro', 'ubuntu')
        tiny_deploy = vol_count == 1
        no_install = tiny_deploy or man.runway_options.get('no_install') == 'True'
        no_snap = no_install or man.runway_options.get('no_snapshot') == 'True'

        # starting from a base image doesn't work if the base image
        # has fewer drives than the current manifest you're loading
        run_command("./make_base_container.sh "
                    "{} {} {} {} {}{}".format(distro, container_name, base_image,
                                              vol_size, vol_count, debug_string), RUNWAY_DIR)

        setup_and_run_ansible_on_guest.setup_and_run_ansible(container_name, debug=debug, drive_count=vol_count)

        if not no_install:
            run_command("./generic_installer.py {}".format(container_name),
                        RUNWAY_DIR)
        if not no_snap:
            run_command("./snapshot_created_container.sh "
                        "{} {}{}".format(container_name, base_image, debug_string),
                        RUNWAY_DIR)
    except Exception as e:
        colorprint.error(str(e))
        sys.exit(1)

    colorprint.success("Container '{}' successfully "
                       "created.\n".format(container_name))
