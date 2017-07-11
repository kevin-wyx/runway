#!/usr/bin/env python

import argparse
import glob
import os
import sys

from runway_utils import colorprint
from runway_utils.manifest import Manifest
from shutil import copyfile

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
RUNWAY_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
COMPONENTS_DIR = os.path.join(RUNWAY_DIR, 'components')
WORKSPACE_DIR = os.path.join(RUNWAY_DIR, 'guest_workspaces')
WORKSPACE_PREFIX = 'runway-'
DEFAULT_MANIFEST_NAME = 'default_manifest.cfg'
DEFAULT_MANIFEST_PATH = os.path.join(RUNWAY_DIR, DEFAULT_MANIFEST_NAME)
MANIFEST_COPY_NAME = 'manifest.cfg'
MAXIMUM_WORKSPACE_COUNT = 999


def exit_on_error(error_text):
    colorprint.error(error_text)
    colorprint.error("\nIf you want to cleanup your runway installation, run "
                     "'{}'".format(os.path.join(RUNWAY_DIR, 'bin',
                                                'cleanup_runway.sh')))
    sys.exit(1)


def get_maximum_workspace_index_length():
    return len(str(MAXIMUM_WORKSPACE_COUNT))


def get_last_workspace_index():
    wildcard_expression = os.path.join(WORKSPACE_DIR,
                                       '{}'.format(WORKSPACE_PREFIX))
    for i in xrange(get_maximum_workspace_index_length()):
        wildcard_expression += "[0-9]"
    current_workspaces = sorted([os.path.basename(name) for name in
                                 glob.glob(wildcard_expression)], reverse=True)
    if len(current_workspaces) == 0:
        return None
    last_index = int(current_workspaces[0][len(WORKSPACE_PREFIX):])
    return last_index


def get_new_workspace_name():
    last_index = get_last_workspace_index()
    if last_index is None:
        new_index = 1
    elif last_index < MAXIMUM_WORKSPACE_COUNT:
        new_index = last_index + 1
    else:
        raise Exception("You have reached the maximum workspace index "
                        "({}).".format(MAXIMUM_WORKSPACE_COUNT))
    return "{}{:03d}".format(WORKSPACE_PREFIX, new_index)


def create_workspace_dir(workspace_name=None):
    if workspace_name is None:
        # Get name for our new workspace
        user_provided_workspace = False
        try:
            workspace_name = get_new_workspace_name()
        except Exception as e:
            exit_on_error(e.message)
    else:
        user_provided_workspace = True

    new_workspace_path = os.path.join(WORKSPACE_DIR, workspace_name)
    try:
        os.mkdir(new_workspace_path)
    except OSError as e:
        # If the user provided the workspace name, he might be trying to update
        # it, so it's fine if we get error 17 (File exists).
        if not user_provided_workspace or e.errno != 17:
            exit_on_error("Could not create directory '{}': [Errno {}] "
                          "{}".format(new_workspace_path, e.errno, e.strerror))

    return new_workspace_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # TODO: Remove -c option. It's only been created to make all of this usable
    # in the master branch before we get the whole workspaces thing working
    parser.add_argument('-c', '--use_components_dir', action='store_true',
                        default=False, help="Install components into "
                                            "components directory instead of "
                                            "creating a workspace")
    parser.add_argument('-m', '--manifest', default=DEFAULT_MANIFEST_PATH,
                        help="Path to manifest file. Default: '/path"
                             "/to/runway/{}'".format(DEFAULT_MANIFEST_NAME))
    parser.add_argument('-w', '--workspace', default=None,
                        help="Workspace name")

    args = parser.parse_args()
    manifest_file = os.path.abspath(args.manifest)
    use_components_dir = args.use_components_dir
    workspace_name = args.workspace

    if use_components_dir:
        new_workspace_path = COMPONENTS_DIR
    else:
        # Create new workspace directory
        new_workspace_path = create_workspace_dir(workspace_name)

    colorprint.info("\nRetrieving components into workspace at '{}'..."
                    "\n".format(new_workspace_path))

    # Copy manifest into workspace
    copyfile(manifest_file, os.path.join(new_workspace_path,
                                         MANIFEST_COPY_NAME))

    # Retrieve contents
    try:
        current_manifest = Manifest(manifest_file, new_workspace_path)
        current_manifest.retrieve_components()
    except Exception as e:
        exit_on_error(e.message)

    colorprint.success("Guest workspace successfully set up at "
                       "'{}'.".format(new_workspace_path))
