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
        debug_string = " --debug" if man.runway_options.get('debug') == 'True' else ""
        vol_count = man.runway_options['number_of_drives']
        distro = man.runway_options.get('distro', 'ubuntu')

        run_command("./make_base_container.sh "
                    "{} {} {} {} {}{}".format(distro, container_name, base_image,
                                              vol_size, vol_count, debug_string), RUNWAY_DIR)
        run_command("./setup_and_run_ansible_on_guest.sh "
                    "{}{}".format(container_name, debug_string), RUNWAY_DIR)
        # can we determine if we should install based on the manifest
        # or based on the existing images?
        run_command("./generic_installer.py {}".format(container_name),
                    RUNWAY_DIR)
        # run_command("./snapshot_created_container.sh "
        #             "{} {}{}".format(container_name, base_image, debug_string),
        #             RUNWAY_DIR)
    except Exception as e:
        colorprint.error(str(e))
        sys.exit(1)

    colorprint.success("Container '{}' successfully "
                       "created.\n".format(container_name))
