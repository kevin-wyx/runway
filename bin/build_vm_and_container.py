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
DEFAULT_CONFIG_FILE_NAME = 'default_manifest.cfg'
DEFAULT_CONFIG_FILE_PATH = os.path.join(RUNWAY_DIR, DEFAULT_CONFIG_FILE_NAME)

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
    print cmd
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


def get_config_options(config_items):
    checkout_info = {}
    for (key, value) in config_items:
        checkout_info[key] = value
    return checkout_info


def validate_config_options(config_options, section):
    if sum(["branch" in config_options, "sha" in config_options,
            "tag" in config_options]) > 1:
        print_error("You can only specify one of these options: branch, "
                    "sha, tag")
        sys.exit(1)
    if not "url" in config_options:
        print("Error: url not found for {}".format(section))
        sys.exit(1)


def install_components(config):
    for section in config.sections():
        print("Installing {}...".format(section))
        checkout_info = get_config_options(config.items(section))
        validate_config_options(checkout_info, section)

        # Run any needed command BEFORE cloning
        if "pre_cmd" in checkout_info:
            run_command(checkout_info["pre_cmd"], cwd=COMPONENTS_DIR)

        # Clone
        git_cmd = "git clone"
        if "branch" in checkout_info:
            git_cmd += " -b {}".format(checkout_info["branch"])
        git_cmd += " {}".format(checkout_info["url"])
        if "destname" in checkout_info:
            destpath = os.path.join(COMPONENTS_DIR, checkout_info["destname"])
            git_cmd += " {}".format(destpath)

        run_command(git_cmd, cwd=COMPONENTS_DIR)

        # Git checkout in case "sha" or "tag" option is present
        if "sha" in checkout_info or "tag" in checkout_info:
            if not "destname" in checkout_info:
                destpath = os.path.join(COMPONENTS_DIR,
                                        get_repo_name_from_url(
                                            checkout_info["url"]))
            git_cmd = "git checkout "
            if "tag" in checkout_info:
                tag = checkout_info["tag"]
                git_cmd += "tags/{}".format(tag)
            else:
                git_cmd += checkout_info["sha"]

            print_debug(git_cmd)
            print_debug(destpath)
            run_command(git_cmd, destpath)

        # Run any needed command AFTER cloning
        if "post_cmd" in checkout_info:
            run_command(checkout_info["post_cmd"], cwd=COMPONENTS_DIR)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default=DEFAULT_CONFIG_FILE_PATH,
                        help="Path to components config file. Default: '/path"
                             "/to/runway/{}'".format(DEFAULT_CONFIG_FILE_NAME))
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
    install_components(config)

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
    # run_command("./bin/bash_on_current_container.sh", cwd=RUNWAY_DIR)
    print_success("Your new container is now up and running! If you want to "
                  "log into it, just run the following command from the "
                  "runway directory:\n\n\tbin/bash_on_current_container.sh")
