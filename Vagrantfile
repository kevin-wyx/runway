# -*- mode: ruby -*-
# vi: set ft=ruby :

def colorize(text, color_code)
  "\e[#{color_code}m#{text}\e[0m\n"
end

def bold(text)
  "\e[1m#{text}\e[0m\n"
end

def red(text); colorize(text, 31); end
def green(text); colorize(text, 32); end
def yellow(text); colorize(text, 33); end
def blue(text); colorize(text, 34); end
def pink(text); colorize(text, 35); end
def light_blue(text); colorize(text, 36); end

def info(text)
  puts bold(text)
end

def warning(text)
  puts yellow(text)
end

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.provider :virtualbox do |vb|
    vb.name = "runway"
    vb.cpus = Integer(ENV['VAGRANT_CPUS'] || 2)
    vb.memory = Integer(ENV['VAGRANT_RAM'] || 4096)

    # Disk management
    controller_name = (ENV['CONTROLLER_NAME'] || "SCSI")
    if ENV.has_key?('CONTROLLER_NAME')
        info "CONTROLLER_NAME env var detected (#{controller_name})"
    else
        warning "WARNING: CONTROLLER_NAME env var hasn't been set. If you fail to 'vagrant up' your VM, open VirtualBox, check the name of your SCSI Controller and provide it in the CONTROLLER_NAME env var."
    end
    file_to_disk = File.join(File.dirname(File.expand_path(__FILE__)), "SwiftDisk.vmdk")
    unless File.exist?(file_to_disk)
      vb.customize [ "createmedium", "disk", "--filename", file_to_disk, "--format", "vmdk", "--size", 1024 * 10 ]
    end
    vb.customize [ "storageattach", :id , "--storagectl", controller_name, "--port", 2, "--device", 0, "--type", "hdd", "--medium", file_to_disk]
  end

  # Bootstrapping
  config.vm.provision "shell", path: "vagrant_bootstrap.sh"
end
