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

```

Components options
------------------

For every component/section, there is only one mandatory parameter: `url`. But
there are a lot of other options you can specify on order to exactly tell
runway where in the source tree you want to be. Here's a list of available
options:

* `branch`: branch to checkout. Can't be used together with `sha` or `tag`.
* `dest_path`: name for the directory where the repo will be cloned.
* `pre_cmd`: command to run *before* we clone the repo. It will be run from the
`components` directory. It won't be run if the repo had already been cloned.
* `post_cmd`: command to run *after* we get the repo. It will be run from the
`components` directory. It won't be run if the repo had already been cloned.
* `sha`: sha to checkout. Can't be used together with `branch` or `tag`.
* `tag`: tag to checkout. Can't be used together with `branch` or `sha`.
* `url` (mandatory): URL for the repo you want to use.
