#!/usr/bin/env python3

import sys

from libs.cli import run_command


def setup_and_run_ansible(cname, debug=False, no_install=False):
    if not no_install:
        # get all the guest-executed stuff pushed over
        # lxc file push ./ansible/ $CNAME/root/
        # unfortunately, lxc doesn't support directly pushing a whole directory
        # https://github.com/lxc/lxd/issues/1218
        cmd = 'tar cf - ansible | lxc exec %s -- tar xf - -C /root/' % cname
        run_command(cmd, cwd=sys.path[0], shell=True)

        # install ansible
        cmd = 'lxc exec %s -- /bin/bash /root/ansible/install_ansible.sh%s' \
              % (cname, (' --debug' if debug else ''))
        run_command(cmd)

    extra_vars = '-e no_install=true -e tiny_install=true'

    # run bootstrap playbook
    # see http://docs.ansible.com/ansible/latest/playbooks_variables.html#passing-variables-on-the-command-line
    # for passing in a list of drives
    cmd = 'lxc exec %s -- ansible-playbook -i "localhost," -c local %s /root/ansible/bootstrap.yaml' % (cname, extra_vars)
    run_command(cmd)

    # create shared code folder
    cmd = 'lxc config device add %(cname)s sharedcomponents disk ' \
          'path=/home/swift/code source=%(dir)s/guest_workspaces/%(cname)s' \
          % {'cname': cname, 'dir': sys.path[0]}
    run_command(cmd, cwd=sys.path[0])

    # install
    if not no_install:
        cmd = 'lxc exec %s -- ansible-playbook -i "localhost," -c local %s ' \
              '/root/ansible/master_playbook.yaml' % (cname, extra_vars)
        run_command(cmd)


def main():
    cname = sys.argv[1]
    debug = '--debug' in sys.argv
    no_install = '--no-install' in sys.argv

    # TODO
    # need to accept "tiny_mode" and also (list of drives or number of drives)

    setup_and_run_ansible(cname, debug=debug, no_install=no_install)

if __name__ == '__main__':
    main()
