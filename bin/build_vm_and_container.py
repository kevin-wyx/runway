#!/usr/bin/env python

import argparse
import os
import sys

from runway_utils import colorprint
from runway_utils.cli import run_command
from runway_utils.manifest import Manifest

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
RUNWAY_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
WORKSPACE_DIR = os.path.join(RUNWAY_DIR, 'components')
DEFAULT_MANIFEST_NAME = 'default_manifest.cfg'
DEFAULT_MANIFEST_PATH = os.path.join(RUNWAY_DIR, DEFAULT_MANIFEST_NAME)


def exit_on_error(error_text):
    colorprint.error(error_text)
    colorprint.error("\nIf you want to cleanup your runway installation, run "
                     "'{}'".format(os.path.join(RUNWAY_DIR, 'bin',
                                                'cleanup_runway.sh')))
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default=DEFAULT_MANIFEST_PATH,
                        help="Path to manifest file. Default: '/path"
                             "/to/runway/{}'".format(DEFAULT_MANIFEST_NAME))
    parser.add_argument('-u', '--do_not_update_box', action='store_true',
                        default=False, help="Do not try to update Vagrant box")

    args = parser.parse_args()
    config_file = os.path.abspath(args.config)
    update_box = not args.do_not_update_box

    try:
        current_manifest = Manifest(config_file, WORKSPACE_DIR)
        current_manifest.retrieve_components()
    except Exception as e:
        exit_on_error(e.message)

    if update_box:
        colorprint.info("We will keep updating the box until we get a stable "
                   "release...")
        try:
            run_command("vagrant box update --box ubuntu/xenial64",
                        cwd=RUNWAY_DIR)
        except Exception as e:
            exit_on_error(e.message)
        colorprint.info("But we will keep our disks free of old boxes. ;)")
        try:
            run_command("vagrant box prune --name ubuntu/xenial64",
                        cwd=RUNWAY_DIR)
        except Exception as e:
            exit_on_error(e.message)
    else:
        colorprint.info("Skipping box update")

    if os.environ.get('CONTROLLER_NAME') is None:
        colorprint.warning("WARNING: CONTROLLER_NAME env var hasn't been set. If "
                      "you fail to 'vagrant up' your VM, open VirtualBox, "
                      "check the name of your SCSI Controller and provide it "
                      "in the CONTROLLER_NAME env var.")
    try:
        run_command("vagrant up", cwd=RUNWAY_DIR)
    except Exception as e:
        exit_on_error(e.message)

    # Log into our brand new container?
    colorprint.success("Your new container is now up and running! If you want to "
                  "log into it, just run the following command from the "
                  "runway directory:\n\n\tbin/bash_on_current_container.sh")
