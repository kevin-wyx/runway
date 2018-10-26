#!/usr/bin/env python

import os
import subprocess
import sys

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
RUNWAY_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
BIN_DIR = os.path.abspath(os.path.join(RUNWAY_DIR, 'bin'))


def reformat_output(output):
    lines = output.split("\r\n")
    containers = []
    container_info = ""
    for line in lines:
        if not line:
            continue
        clean_line = line.split(" ")[0]
        if "," in clean_line:
            if container_info:
                containers.append(container_info)
            container_info = clean_line.replace('"',"")
        else:
            container_info += ",{}".format(clean_line.replace('"',""))
    if container_info:
        containers.append(container_info)

    return "\n".join(containers)


try:
    container_name = sys.argv[1]
except IndexError:
    print('Usage: %s container_name' % sys.argv[0])
    sys.exit(1)

cmd = "OPTIONALRUNWAYCNAME=1 QUIET=1 source " \
      "lib/get_container_connection_options.sh && ssh -q -t " \
      "${VAGRANTOPTIONS} ${RUNWAYHOST} lxc list %s -c n4 --format " \
      "csv" % container_name
output = subprocess.check_output(cmd, shell=True, cwd=BIN_DIR)
print(reformat_output(output))
