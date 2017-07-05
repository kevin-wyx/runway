#!/usr/bin/env python

import argparse
import ConfigParser
import os
import re
import subprocess
import shlex
import sys

from subprocess import CalledProcessError

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
RUNWAY_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
COMPONENTS_DIR = os.path.join(RUNWAY_DIR, 'components')
DEFAULT_MANIFEST_NAME = 'default_manifest.cfg'
DEFAULT_MANIFEST_PATH = os.path.join(RUNWAY_DIR, DEFAULT_MANIFEST_NAME)

class bcolors:
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def colorize(text, color):
    return "{}{}{}".format(color, text, bcolors.ENDC)


def print_debug(text):
    print(colorize(text, bcolors.BLUE))


def print_error(text):
    print(colorize(text, bcolors.RED))


def print_info(text):
    print(colorize(text, bcolors.BOLD))


def print_success(text):
    print(colorize(text, bcolors.GREEN))


def print_warning(text):
    print(colorize(text, bcolors.YELLOW))


def extract_env_vars(cmd):
    env_vars = {}
    matches = re.split('(\S+=\S+) ', cmd)
    remaining_matches = list(matches)
    for match in matches:
        stripped_match = match.strip()
        if stripped_match != '':
            if match.find(' ') > -1 or match.find('=') < 0:
                break
            else:
                split_match = stripped_match.split('=')
                env_vars[split_match[0]] = split_match[1]
        remaining_matches.pop(0)
    remainder = ''.join(remaining_matches)
    return env_vars if len(env_vars) > 0 else None, remainder


def run_command(cmd, cwd=None):
    print("$ {}".format(cmd))
    env_vars, stripped_cmd = extract_env_vars(cmd)
    try:
        p = subprocess.Popen(shlex.split(stripped_cmd),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             cwd=cwd,
                             env=env_vars,
                             bufsize=1)
        for line in iter(p.stdout.readline, ""):
            print(line.decode('utf-8').rstrip())
        exit_code = p.wait()
        if exit_code != 0:
            print_error("Command '{}' responded with a non-zero exit status "
                        "({}).".format(cmd, exit_code))
            print_error("An error for this command might have been printed "
                        "above these lines. Please read the output in order "
                        "to check what went wrong.")
            print_error("If you want to cleanup your runway installation, run "
                        "'{}'".format(os.path.join(RUNWAY_DIR, 'bin',
                                                   'cleanup_runway.sh')))
            sys.exit(1)
    except CalledProcessError as e:
        print_error("Error running '{}':\n{}\n{}".format(cmd, e.output,
                                                         e.message))
        print_error("If you want to cleanup your runway installation, run "
                    "'{}'".format(os.path.join(RUNWAY_DIR, 'bin',
                                               'cleanup_runway.sh')))
        sys.exit(1)
    except Exception as e:
        print_error("Error running '{}':\n{}".format(cmd, e.message))
        print_error(e)
        print_error("If you want to cleanup your runway installation, run "
                    "'{}'".format(os.path.join(RUNWAY_DIR, 'bin',
                                               'cleanup_runway.sh')))
        sys.exit(1)


def get_repo_name_from_url(url):
    result = re.match('^.+\/(.+)\.git$', url)
    if result is None:
        print_error("Couldn't get the name of the repo.")
        sys.exit(1)
    return result.group(1)


def get_config_options(config, section):
    config_options = {}
    boolean_options = ["local"]
    for (key, value) in config.items(section):
        if key in boolean_options:
            try:
                config_options[key] = config.getboolean(section, key)
            except ValueError:
                print_error("Component '{}' has an invalid value for boolean "
                            "option '{}'.\nValid values for 'true' are: '1', "
                            "'yes', 'true', and 'on'.\nValid values for "
                            "'false' are: '0', 'no', 'false', and 'off'.\nThe "
                            "values are case insensitive.".format(section,
                                                                  key))
                sys.exit(22)  # EINVAL (22): Invalid argument. Is that ok?
        else:
            config_options[key] = value
    for option in boolean_options:
        if not option in config_options:
            config_options[option] = False
    return config_options


def validate_config_options(config_options, section):
    if sum(["branch" in config_options, "sha" in config_options,
            "tag" in config_options]) > 1:
        print_error("You can only specify one of these options: branch, "
                    "sha, tag")
        sys.exit(1)
    if config_options["local"] and not "dest_path" in config_options:
        print_error("You need to specify a 'dest_path' for local '{}' "
                    "component.".format(section))
        sys.exit(1)
    if not config_options["local"] and not "url" in config_options:
        print_error("Error: url not found for {}".format(section))
        sys.exit(1)


def get_dest_path(config_options):
    if "dest_path" in config_options:
        return os.path.join(COMPONENTS_DIR, config_options["dest_path"])
    else:
        return os.path.join(COMPONENTS_DIR, get_repo_name_from_url(
            config_options["url"]))


def git_clone_component(config_options):
    # Clone
    git_cmd = "git clone"
    if "branch" in config_options:
        git_cmd += " -b {}".format(config_options["branch"])
    git_cmd += " {}".format(config_options["url"])
    if "dest_path" in config_options:
        dest_path = os.path.join(COMPONENTS_DIR, config_options["dest_path"])
        git_cmd += " {}".format(dest_path)

    run_command(git_cmd, cwd=COMPONENTS_DIR)


def git_checkout_and_pull_component(config_options, dest_path):
    git_cmd = "git checkout "
    if "tag" in config_options:
        git_cmd += "tags/{}".format(config_options["tag"])
    elif "sha" in config_options:
        git_cmd += config_options["sha"]
    elif "branch" in config_options:
        git_cmd += config_options["branch"]

    run_command(git_cmd, dest_path)
    run_command("git pull", dest_path)


def get_components(config):
    for section in config.sections():
        print_info("Getting {}...".format(section))
        config_options = get_config_options(config, section)
        validate_config_options(config_options, section)
        dest_path = get_dest_path(config_options)
        component_exists = os.path.isdir(dest_path)

        # Run any needed command BEFORE cloning
        if not component_exists and "pre_cmd" in config_options:
            run_command(config_options["pre_cmd"], cwd=COMPONENTS_DIR)

        if not config_options["local"]:
            if not component_exists:
                git_clone_component(config_options)

            # Git checkout + pull in case "sha" or "tag" option is present or
            # if the component directory already existed.
            if component_exists or "sha" in config_options or \
                            "tag" in config_options:
                git_checkout_and_pull_component(config_options, dest_path)
        else:
            if not component_exists:
                print_error("Component '{}' has been marked as local, but it "
                            "doesn't exist.".format(section))
            else:
                print("Component '{}' is locally managed.".format(section))

        # Run any needed command AFTER cloning
        if not component_exists and "post_cmd" in config_options:
            run_command(config_options["post_cmd"], cwd=COMPONENTS_DIR)

        # Just print a new line to keep components' output separated
        print("")


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

    if not os.path.isfile(config_file):
        print("Error: file {} does not exist.".format(config_file))
        sys.exit(1)

    config = ConfigParser.ConfigParser()
    config.read(config_file)
    get_components(config)

    if update_box:
        print_info("We will keep updating the box until we get a stable "
                   "release...")
        run_command("vagrant box update --box ubuntu/xenial64", cwd=RUNWAY_DIR)
        print_info("But we will keep our disks free of old boxes. ;)")
        run_command("vagrant box prune --name ubuntu/xenial64", cwd=RUNWAY_DIR)
    else:
        print_info("Skipping box update")
    if os.environ.get('CONTROLLER_NAME') is None:
        print_warning("WARNING: CONTROLLER_NAME env var hasn't been set. If "
                      "you fail to 'vagrant up' your VM, open VirtualBox, "
                      "check the name of your SCSI Controller and provide it "
                      "in the CONTROLLER_NAME env var.")
    run_command("vagrant up", cwd=RUNWAY_DIR)

    # Log into our brand new container?
    print_success("Your new container is now up and running! If you want to "
                  "log into it, just run the following command from the "
                  "runway directory:\n\n\tbin/bash_on_current_container.sh")
