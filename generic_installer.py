#!/usr/bin/env python3

# find every code repo in /home/swift/code on the given container
# then find if it has an `install.sh` file
# if so, execute it
# exclode libec, swiftclient, and swift


import os
import sys
import shlex
import subprocess

container_name = sys.argv[1]

found_repos = []
for entry in os.scandir('components'):
    if entry.is_dir() and entry.name not in ('swift',
                                             'python-swiftclient',
                                             'liberasurecode') and \
            os.path.isfile('components/{}/install.sh'.format(entry.name)):
        found_repos.append(entry.name)

for repo_path in found_repos:
    cmd = 'lxc exec {} -- /bin/bash /home/swift/code/{}/install.sh'.format(
        container_name, repo_path)
    print(cmd)
    try:
        p = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, check=True)

        # catch/log errors
        print('stdout:\n{}'.format(p.stdout.decode()))
        print('\n\nstderr:\n{}'.format(p.stderr.decode()))
    except subprocess.CalledProcessError as e:
        print("{} installer script exited with non-zero status {}".format(
            repo_path, e.returncode))
        print('stdout:\n{}'.format(e.stdout.decode()))
        print('\n\nstderr:\n{}'.format(e.stderr.decode()))
        sys.exit(e.returncode)
