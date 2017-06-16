# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.provider :virtualbox do |vb|
    vb.name = "runway"
    vb.cpus = Integer(ENV['VAGRANT_CPUS'] || 2)
    vb.memory = Integer(ENV['VAGRANT_RAM'] || 4096)

    file_to_disk = "SwiftDisk.vmdk"
    unless File.exist?(file_to_disk)
      vb.customize [ "createmedium", "disk", "--filename", file_to_disk, "--format", "vmdk", "--size", 1024 * 10 ]
    end
    vb.customize [ "storageattach", :id , "--storagectl", "SCSI", "--port", 2, "--device", 0, "--type", "hdd", "--medium", file_to_disk]
  end
end
