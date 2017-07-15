How to create manifest files
============================

Manifest files use standard config/ini files syntax. Every section is a
component that you want to checkout (with Git).

A typical manifest file might look like this:

```ini
[runway]
family = ProxyFS

[swift]
url = git@github.com:swiftstack/swift.git
branch = master

[liberasurecode]
url = git@github.com:openstack/liberasurecode.git
branch = master

[python-swiftclient]
url = git@github.com:openstack/python-swiftclient.git
branch = master

[proxyfs-functional-tests]
url = git@github.com:swiftstack/proxyfs-functional-tests.git
dest_path = functional-tests

[ProxyFS]
url = git@github.com:swiftstack/ProxyFS.git
branch = development
dest_path = ProxyFS/src/github.com/swiftstack/ProxyFS
install = ci/ansible/install_proxyfs.sh runway

[conf]
url = git@github.com:swiftstack/conf.git
dest_path = ProxyFS/src/github.com/swiftstack/conf

[cstruct]
url = git@github.com:swiftstack/cstruct.git
dest_path = ProxyFS/src/github.com/swiftstack/cstruct

[sortedmap]
url = git@github.com:swiftstack/sortedmap.git
dest_path = ProxyFS/src/github.com/swiftstack/sortedmap

[my-local-component]
local = true
dest_path = my-super-secret-project

[ProxyFSAlternative]
url = git@github.com:swiftstack/ProxyFS.git
branch = development
dest_path = ProxyFSAlternative/src/github.com/swiftstack/ProxyFS
post_cmd = cp -rf ./ProxyFS/src/github.com/swiftstack/ProxyFS/ci/ansible/install_proxyfs_runway.sh ./ProxyFS/install.sh
```


Runway options
--------------

Any configuration option that affects how runway runs, will be included in the
`runway` section. Adding a `runway` section is completely optional, and so is
adding any configuration options inside this section.

\* For now, we only have one option, but the set of possible options will grow in
the future.

Here's a list of available options:

* `family` (string): If this option is provided, runway will try to create
containers based on a snapshot using that same family name. If none is found,
it will create a new container from scratch and a new snapshot based on it.


Components options
------------------

There are quite a few options you can specify in order to exactly tell Runway
how to manage each component. Some of the options have dependencies between
each other, so please, read this documentation carefully.

Here's a list of available options:

* `branch` (string): Branch to checkout. Can't be used together with `sha` or
`tag`.
* `dest_path` (string): Relative path from Runway's `components` directory to
the component's directory. It is mandatory when `local` is `true`.
* `local` (boolean): Whether or not the component is a local component. Local
components won't be automatically managed. It's the user's responsability to
keep them up to date. Runway will try to install it anyway. The default value
is `false`.
* `install` (string): Command to run to install the component. It will be run
from the component's top level directory. If `install` option is not specified,
Runway will try to find an `install.sh` script in the component's root
directory. If no installation is needed, you can just not provide an install
command/script.
* `pre_cmd` (string): Command to run *before* we clone the repo. It will be run
from the `components` directory. It won't be run if the repo had already been
cloned or if it's a local component.
* `post_cmd` (string): Command to run *after* we get the repo. It will be run
from the `components` directory. It won't be run if the repo had already been
cloned or if it's a local component.
* `sha` (string): SHA to checkout. Can't be used together with `branch` or
`tag`.
* `tag` (string): Tag to checkout. Can't be used together with `branch` or
`sha`.
* `url` (string): URL for the repo you want to use. It will be ignored if
`local` is `true`. It is mandatory when `local` is `false`.


\* Valid values for `true` booleans are: `1`, `yes`, `true`, and `on`.

\* Valid values for `false` booleans are: `0`, `no`, `false`, and `off`.

\* Boolean values are case insensitive.