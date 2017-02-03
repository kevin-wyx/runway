#!/usr/bin/env python3

import subprocess
import shlex
import sys
import os.path


CNAME = sys.argv[1]
VOLUME_GROUP = sys.argv[2]

dev_numbers = {}

for i in range(8):
    # this can give an error. how do we suppress?
    create_command = "lvcreate -y --size 10G --name '%s-vol%s' %s" % (CNAME, i, VOLUME_GROUP)
    p = subprocess.run(shlex.split(create_command), stdout=subprocess.PIPE)
    display_command = "lvdisplay '/dev/%s/%s-vol%s'" % (VOLUME_GROUP, CNAME, i)
    p = subprocess.run(shlex.split(display_command), stdout=subprocess.PIPE)
    for line in p.stdout.decode().split('\n'):
        if 'Block device' in line:
            maj_min = line.split()[2].strip()
            major, minor = maj_min.split(':')
            dev_numbers['minor%d' % i] = minor
            dev_numbers['major%d' % i] = major

path_to_repo = os.path.dirname(os.path.realpath(__file__))

template_vars = {}
template_vars.update(dev_numbers)
template_vars['path_to_shared_code'] = path_to_repo + '/guest_workspaces/%s_shared_code/' % CNAME

template_file = 'container_base/swift-runway-v1.tmpl'
raw = open(template_file).read()
formatted = raw.format(name="%s-profile" % CNAME, **template_vars)
print(formatted)
