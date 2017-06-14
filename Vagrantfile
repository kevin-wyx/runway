# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.provider :virtualbox do |vb|
     vb.name = "runway"
     vb.cpus = Integer(ENV['VAGRANT_CPUS'] || 2)
     vb.memory = Integer(ENV['VAGRANT_RAM'] || 4096)
  end
end
