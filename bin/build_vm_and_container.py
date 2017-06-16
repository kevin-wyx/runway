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
DEFAULT_CONFIG_FILE_NAME = 'default_components.cfg'
DEFAULT_CONFIG_FILE_PATH = os.path.join(RUNWAY_DIR, DEFAULT_CONFIG_FILE_NAME)


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
    except CalledProcessError as e:
        print("Error running '{}':\n{}\n{}".format(cmd, e.output, e.message))
        print("If you want to cleanup your runway installation, run "
              "{}".format(os.path.join(RUNWAY_DIR, 'bin',
                                       'cleanup_runway.sh')))
        sys.exit(1)
    except Exception as e:
        print("Error running '{}':\n{}".format(cmd, e.message))
        print("If you want to cleanup your runway installation, run "
              "{}".format(os.path.join(RUNWAY_DIR, 'bin',
                                       'cleanup_runway.sh')))
        sys.exit(1)


def install_components(config):
    for section in config.sections():
        print("Installing {}...".format(section))
        checkout_info = {}
        for (key, value) in config.items(section):
            checkout_info[key] = value
        if not "url" in checkout_info:
            print("Error: url not found for {}".format(section))
            sys.exit(1)
        if "pre_cmd" in checkout_info:
            run_command(checkout_info["pre_cmd"], cwd=COMPONENTS_DIR)
        git_cmd = "git clone"
        if "branch" in checkout_info:
            git_cmd += " -b {}".format(checkout_info["branch"])
        git_cmd += " {}".format(checkout_info["url"])
        if "destname" in checkout_info:
            git_cmd += " {}".format(os.path.join(COMPONENTS_DIR,
                                                 checkout_info["destname"]))
        run_command(git_cmd, cwd=COMPONENTS_DIR)
        if "post_cmd" in checkout_info:
            run_command(checkout_info["post_cmd"], cwd=COMPONENTS_DIR)


parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', default=DEFAULT_CONFIG_FILE_PATH,
                    help="Path to components config file. Default: '/path/to"
                         "/runway/{}'".format(DEFAULT_CONFIG_FILE_NAME))

args = parser.parse_args()
config_file = os.path.abspath(args.config)

if not os.path.isfile(config_file):
    print("Error: file {} does not exist.".format(config_file))
    sys.exit(1)

config = ConfigParser.ConfigParser()
config.read(config_file)
install_components(config)

run_command("vagrant up", cwd=RUNWAY_DIR)
run_command("vagrant halt", cwd=RUNWAY_DIR)
print("This is a WIP. TODO: add disk with Vagrantfile, setup LVM and run runway itself.")
