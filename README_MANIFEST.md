How to create manifest files
============================

Manifest files use standard config/ini files syntax. Every section is a
component that you want to checkout (with Git).

A typical manifest file might look like this:

```ini
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
post_cmd = cp -rf ./ProxyFS/src/github.com/swiftstack/ProxyFS/ci/ansible/install_proxyfs_runway.sh ./ProxyFS/install.sh

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
```

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
keep them up to date. Runway will try to install it anyway if it has an
`install.sh` script in its root directory. The default value is `false`.
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
