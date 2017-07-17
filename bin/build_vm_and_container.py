#!/usr/bin/env python

import argparse
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..')))

from libs import colorprint
from libs.cli import run_command

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
RUNWAY_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
BIN_DIR = os.path.abspath(os.path.join(RUNWAY_DIR, 'bin'))
SETUP_WORKSPACE_SCRIPT = 'setup_guest_workspace.py'
VAGRANT_BOX_NAME = "ubuntu/xenial64"


def exit_on_error(error_text):
    colorprint.error(error_text)
    colorprint.error("\nIf you want to cleanup your runway installation, run "
                     "'{}'".format(os.path.join(RUNWAY_DIR, 'bin',
                                                'cleanup_runway.sh')))
    sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--manifest', default=None,
                        help="Path to manifest file. Run '{}/{} -h' to check "
                             "the default manifest "
                             "file.".format(BIN_DIR, SETUP_WORKSPACE_SCRIPT))
    parser.add_argument('-u', '--do_not_update_box', action='store_true',
                        default=False, help="Do not try to update Vagrant box")
    parser.add_argument('-w', '--workspace', default=None,
                        help="Workspace name")

    args = parser.parse_args()
    manifest_file = os.path.abspath(args.manifest) \
        if args.manifest is not None else None
    update_box = not args.do_not_update_box
    workspace_name = args.workspace

    # Setup workspace
    cmd = "./setup_guest_workspace.py"
    if manifest_file is not None:
        cmd += " -m {}".format(manifest_file)
    if workspace_name is not None:
        cmd += " -w {}".format(workspace_name)
    run_command(cmd, cwd=BIN_DIR)

    # Update Vagrant box
    if update_box:
        colorprint.info("\nWe will keep updating the box until we get a "
                        "stable release...")
        try:
            run_command("vagrant box update --box {}".format(VAGRANT_BOX_NAME),
                        cwd=RUNWAY_DIR)
        except Exception as e:
            colorprint.warning("Vagrant box update failed. If it's your first "
                               "time running this script, it's ok because you "
                               "didn't have the box yet. If it's not your "
                               "first time, maybe we should worry...\n")
        colorprint.info("But we will keep our disks free of old boxes. ;)")
        try:
            run_command("vagrant box prune --name {}".format(VAGRANT_BOX_NAME),
                        cwd=RUNWAY_DIR)
        except Exception as e:
            exit_on_error(e.message)
    else:
        colorprint.info("Skipping box update")

    # Vagrant up
    if os.environ.get('CONTROLLER_NAME') is None:
        colorprint.warning("WARNING: CONTROLLER_NAME env var hasn't been set. "
                           "If you fail to 'vagrant up' your VM, open "
                           "VirtualBox, check the name of your SCSI "
                           "Controller and provide it in the CONTROLLER_NAME "
                           "env var.")
    try:
        run_command("vagrant up", cwd=RUNWAY_DIR)
    except Exception as e:
        exit_on_error(e.message)

    # Log into our brand new container?
    colorprint.success("Your new container is now up and running! If you want "
                       "to log into it, just run the following command from "
                       "the runway directory:\n\n\t"
                       "bin/bash_on_current_container.sh")
