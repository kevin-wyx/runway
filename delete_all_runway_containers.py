#!/usr/bin/env python3

# do lxc list --format=json swift-runway
# ...and delete them


# while it would be cool if this worked, it doesn't and the docs are bad
# https://linuxcontainers.org/lxc/documentation/#python
# import lxc
# for defined in (True, False):
#     for active in (True, False):
#         x = lxc.list_containers(active=active, defined=defined)
#         print(x, '=> lxc.list_containers(active=%s, defined=%s)' % (active, defined))


import json
import subprocess
import shlex

list_command = 'lxc list --format=json'
p = subprocess.run(shlex.split(list_command), stdout=subprocess.PIPE)

containers = json.loads(p.stdout.decode())
to_delete = [x['name'] for x in containers if x['name'].startswith('swift-runway-')]

delete_command = 'lxc delete --force %s' % ' '.join(to_delete)
p = subprocess.run(shlex.split(delete_command))
