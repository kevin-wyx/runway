#!/usr/bin/env python3

import subprocess
import shlex
import sys


CNAME = sys.argv[1]
VOLUME_GROUP = sys.argv[2]

dev_numbers = {}

for i in range(8):
    # this can give an error. how do we suppress?
    create_command = "lvcreate --size 10G --name '%s-vol%s' %s" % (CNAME, i, VOLUME_GROUP)
    p = subprocess.run(shlex.split(create_command), stdout=subprocess.PIPE)
    display_command = "lvdisplay '/dev/%s/%s-vol%s'" % (VOLUME_GROUP, CNAME, i)
    p = subprocess.run(shlex.split(display_command), stdout=subprocess.PIPE)
    for line in p.stdout.decode().split('\n'):
        if 'Block device' in line:
            maj_min = line.split()[2].strip()
            major, minor = maj_min.split(':')
            dev_numbers['minor%d' % i] = minor
            dev_numbers['major%d' % i] = major

template_file = 'container-base/swift-runway-v1.tmpl'
raw = open(template_file).read()
formatted = raw.format(name="%s-profile" % CNAME, **dev_numbers)
print(formatted)
