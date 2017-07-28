#!/usr/bin/env python3

import subprocess
import shlex
import sys
import os.path


CNAME = sys.argv[1]
VOLUME_GROUP = sys.argv[2]
try:
    DRIVE_SIZE = sys.argv[3]
except IndexError:
    DRIVE_SIZE = '1G'
try:
    DRIVE_COUNT = int(sys.argv[4])
except (IndexError, TypeError):
    DRIVE_COUNT = 8

dev_numbers = {}

single_drive_section = '''
  disk%d:
    path: /dev/sd%s
    major: %s
    minor: %s
    type: unix-block
'''.strip('\n')

template_drive_sections = []

for i in range(DRIVE_COUNT):
    drive_letter = chr(ord('b') + i)
    create_command = "lvcreate -y --size %s --name '%s-vol%s' %s" % (DRIVE_SIZE, CNAME, i, VOLUME_GROUP)
    p = subprocess.run(shlex.split(create_command), stdout=subprocess.PIPE)
    #TODO: check return code for errors
    display_command = "lvdisplay '/dev/%s/%s-vol%s'" % (VOLUME_GROUP, CNAME, i)
    p = subprocess.run(shlex.split(display_command), stdout=subprocess.PIPE)
    for line in p.stdout.decode().split('\n'):
        if 'Block device' in line:
            maj_min = line.split()[2].strip()
            major, minor = maj_min.split(':')
            drive = single_drive_section % (i, drive_letter, major, minor)
            template_drive_sections.append(drive)

path_to_repo = os.path.dirname(os.path.realpath(__file__))

template_vars = {}
template_vars.update(dev_numbers)
template_vars['drive_sections'] = '\n'.join(template_drive_sections)

template_file = path_to_repo + '/container_base/swift-runway-ram-v1.tmpl'
raw = open(template_file).read()
formatted = raw.format(name="%s-profile" % CNAME, **template_vars)
print(formatted)
