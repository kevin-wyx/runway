# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.box_version = "20180809.0.0"
  config.vm.box_check_update = false
  config.vm.provider :virtualbox do |vb|
    vb.name = "runway"
    vb.cpus = Integer(ENV['VAGRANT_CPUS'] || 2)
    vb.memory = Integer(ENV['VAGRANT_RAM'] || 4096)

    # Disk management
    controller_name = (ENV['CONTROLLER_NAME'] || "SCSI")
    file_to_disk = File.join(File.dirname(File.expand_path(__FILE__)), "SwiftDisk.vmdk")
    unless File.exist?(file_to_disk)
      # We want to allow 2 equal containers to be created within the same VM
      # Volume size in MiB * number of devices x 2 (max) containers
      vmdk_size = ENV['VOL_SIZE'].to_i * ENV['VOL_COUNT'].to_i * 2
      vb.customize [ "createmedium", "disk", "--filename", file_to_disk, "--format", "vmdk", "--size", vmdk_size ]
    end
    vb.customize [ "storageattach", :id , "--storagectl", controller_name, "--port", 2, "--device", 0, "--type", "hdd", "--medium", file_to_disk]
  end

  # Bootstrapping
  config.vm.provision "shell", env: {'DISTRO' => ENV['DISTRO']}, path: "vagrant_bootstrap.sh"
end
