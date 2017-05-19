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
for entry in os.scandir('components' % container_name):
    if entry.is_dir() and entry.name not in ('swift', 'python-swiftclient', 'liberasurecode'):
        found_repos.append(entry.name)

for repo_path in found_repos:
    cmd = 'lxc exec %s -- /bin/bash /home/swift/code/%s/install.sh' % (container_name, repo_path)
    print(cmd)
    p = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # catch/log errors
    print('stdout:\n%s' % p.stdout.decode())
    print('\n\nstderr:\n%s' % p.stderr.decode())
