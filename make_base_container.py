#!/usr/bin/env python3

import argparse
import os
import sys

from libs import colorprint
from libs.cli import run_command

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
# assume well-known lvm volume group on host
#   ...later we'll figure out how to make this dynamic
DEFAULT_VOL_SIZE = "1G"
DEFAULT_VOL_COUNT = 8
VG_NAME = "swift-runway-vg01"


def exit_with_error(error_text):
    colorprint.error(error_text)
    sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('distro', type=str, help='Container distro')
    parser.add_argument('cname', metavar='containername', help='Container '
                                                               'name')
    parser.add_argument('baseimage', nargs='?',
                        help='Base image. Defaults: \'images:centos/7/amd64\' '
                             'for RHEL distro, \'ubuntu:16.04\' otherwise')
    parser.add_argument('volsize', nargs='?', default=DEFAULT_VOL_SIZE,
                        help='Volume size. Default: '
                             '{}'.format(DEFAULT_VOL_SIZE))
    parser.add_argument('volcount', nargs='?', type=int,
                        default=DEFAULT_VOL_COUNT,
                        help='Volume count. Default: '
                             '{}'.format(DEFAULT_VOL_COUNT))

    args = parser.parse_args()
    distro = args.distro
    container_name = args.cname
    base_image = args.baseimage
    volume_size = args.volsize
    volume_count = args.volcount

    default_image = "images:centos/7/amd64" if distro == "RHEL" \
        else "ubuntu:16.04"

    if base_image is None:
        base_image = default_image

    try:
        # make a container profile that maps 8 block devices to the guest
        run_command("lxc profile create {}-profile".format(container_name))
        run_command("./make_lxc_profile.py {} {} {} {} | "
                    "lxc profile edit {}-profile".format(container_name,
                                                         VG_NAME,
                                                         volume_size,
                                                         volume_count,
                                                         container_name),
                    cwd=SCRIPT_DIR, shell=True)

        # launch the new container
        print("Trying to launch container from base image "
              "{}".format(base_image))
        run_command("lxc launch {} {} -p {}-profile || "
                    "lxc launch {} {} -p {}-profile".format(base_image,
                                                            container_name,
                                                            container_name,
                                                            default_image,
                                                            container_name,
                                                            container_name),
                    shell=True)
    except Exception as e:
        exit_with_error(str(e))
