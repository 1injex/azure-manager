# coding:utf8
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.common.credentials import ServicePrincipalCredentials
import time


def create_credential_object(tenant_id, client_id, client_secret):
    print("Create Credential")
    tenant_id = tenant_id
    client_id = client_id
    client_secret = client_secret
    credential = ServicePrincipalCredentials(tenant=tenant_id, client_id=client_id, secret=client_secret)
    return credential


def create_resource_group(subscription_id, credential, tag, location):
    print("Create Resource Group")
    credential = credential
    resource_client = ResourceManagementClient(credential, subscription_id)
    RESOURCE_GROUP_NAME = tag
    LOCATION = location
    rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
                                                                 {
                                                                     "location": LOCATION
                                                                 }
                                                                 )


def create_or_update_vm(subscription_id, credential, tag, location, username, password, size, os, custom, acc, disk, spot):
    global publisher, offer, sku
    compute_client = ComputeManagementClient(credential, subscription_id)
    RESOURCE_GROUP_NAME = tag
    VNET_NAME = ("vnet-" + tag)
    SUBNET_NAME = ("subnet-" + tag)
    IP_NAME = ("ip-" + tag)
    IP_CONFIG_NAME = ("ipconfig-" + tag)
    NIC_NAME = ("nicname-" + tag)
    LOCATION = location
    VM_NAME = tag
    USERNAME = username
    PASSWORD = password
    SIZE = size
    DISK = disk
    CUSTOM = custom
    ACC = acc
    if spot == "True":
        SPOT = "Spot"
        DELETE = "Delete"
        MAXPRICE = 100000
    else:
        SPOT = ""
        DELETE = ""
        MAXPRICE = ""
    images_list = {
        "Debian_9": {
            "display": "Debian 9",
            "sku": "9",
            "publisher": "credativ",
            "version": "latest",
            "offer": "Debian",
        },
        "Debian_10": {
            "display": "Debian 10 (gen2)",
            "sku": "10-gen2",
            "publisher": "Debian",
            "version": "latest",
            "offer": "debian-10",
        },
        "Debian_11": {
            "display": "Debian 11 (gen2)",
            "sku": "11-gen2",
            "publisher": "Debian",
            "version": "latest",
            "offer": "debian-11",
        },
        "Debian_10_gen1": {
            "display": "Debian 10",
            "sku": "10",
            "publisher": "Debian",
            "version": "latest",
            "offer": "debian-10",
        },
        "Debian_11_gen1": {
            "display": "Debian 11",
            "sku": "11",
            "publisher": "Debian",
            "version": "latest",
            "offer": "debian-11",
        },
        "Ubuntu_16_04": {
            "display": "Ubuntu 16.04 (gen2)",
            "sku": "16_04-lts-gen2",
            "publisher": "Canonical",
            "version": "latest",
            "offer": "UbuntuServer",
        },
        "Ubuntu_18_04": {
            "display": "Ubuntu 18.04 (gen2)",
            "sku": "18_04-lts-gen2",
            "publisher": "Canonical",
            "version": "latest",
            "offer": "UbuntuServer",
        },
        "Ubuntu_20_04": {
            "display": "Ubuntu 20.04 (gen2)",
            "sku": "20_04-lts-gen2",
            "publisher": "Canonical",
            "version": "latest",
            "offer": "0001-com-ubuntu-server-focal",
        },
        "Ubuntu_16_04_gen1": {
            "display": "Ubuntu 16.04",
            "sku": "16.04.0-LTS",
            "publisher": "Canonical",
            "version": "latest",
            "offer": "UbuntuServer",
        },
        "Ubuntu_18_04_gen1": {
            "display": "Ubuntu 18.04",
            "sku": "18.04-LTS",
            "publisher": "Canonical",
            "version": "latest",
            "offer": "UbuntuServer",
        },
        "Ubuntu_20_04_gen1": {
            "display": "Ubuntu 20.04",
            "sku": "20_04-lts",
            "publisher": "Canonical",
            "version": "latest",
            "offer": "0001-com-ubuntu-server-focal",
        },
        "Centos_79": {
            "display": "Centos 7.9 (gen2)",
            "sku": "7_9-gen2",
            "publisher": "OpenLogic",
            "version": "latest",
            "offer": "CentOS",
        },
        "Centos_79_gen1": {
            "display": "Centos 7.9",
            "sku": "7_9",
            "publisher": "OpenLogic",
            "version": "latest",
            "offer": "CentOS",
        },
        "Centos_85": {
            "display": "Centos 8.5 (gen2)",
            "sku": "8_5-gen2",
            "publisher": "OpenLogic",
            "version": "latest",
            "offer": "CentOS",
        },
        "Centos_85_gen1": {
            "display": "Centos 8.5",
            "sku": "8_5",
            "publisher": "OpenLogic",
            "version": "latest",
            "offer": "CentOS",
        },
        "WinData_2022": {
            "display": "Windows Datacenter 2022",
            "sku": "2022-Datacenter-smalldisk",
            "publisher": "MicrosoftWindowsServer",
            "version": "latest",
            "offer": "WindowsServer",
        },
        "WinData_2019": {
            "display": "Windows Datacenter 2019",
            "sku": "2019-Datacenter-smalldisk",
            "publisher": "MicrosoftWindowsServer",
            "version": "latest",
            "offer": "WindowsServer",
        },
        "WinData_2016": {
            "display": "Windows Datacenter 2016",
            "sku": "2016-Datacenter-smalldisk",
            "publisher": "MicrosoftWindowsServer",
            "version": "latest",
            "offer": "WindowsServer",
        },
        "WinData_2012": {
            "display": "Windows Datacenter 2012",
            "sku": "2012-Datacenter-smalldisk",
            "publisher": "MicrosoftWindowsServer",
            "version": "latest",
            "offer": "WindowsServer",
        },
        "WinDesk_10": {
            "display": "Windows 10 21H2 (gen2)",
            "sku": "win10-21h2-pro-zh-cn-g2",
            "publisher": "MicrosoftWindowsDesktop",
            "version": "latest",
            "offer": "Windows-10",
        },
        "WinDesk_11": {
            "display": "Windows 11 21H2",
            "sku": "win11-21h2-pro-zh-cn",
            "publisher": "MicrosoftWindowsDesktop",
            "version": "latest",
            "offer": "Windows-11",
        }
    }

    network_client = NetworkManagementClient(credential, subscription_id)
    try:
        print("Create VNET")
        poller = network_client.virtual_networks.create_or_update(RESOURCE_GROUP_NAME,
                                                                  VNET_NAME,
                                                                  {
                                                                      "location": LOCATION,
                                                                      "address_space": {
                                                                          "address_prefixes": ["10.0.0.0/16"]
                                                                      }
                                                                  }
                                                                  )
        vnet_result = poller.result()
        print("Create Subnets")
        poller = network_client.subnets.create_or_update(RESOURCE_GROUP_NAME,
                                                         VNET_NAME, SUBNET_NAME,
                                                         {"address_prefix": "10.0.0.0/24"}
                                                         )
        subnet_result = poller.result()
        print("Create Public IP")
        poller = network_client.public_ip_addresses.create_or_update(RESOURCE_GROUP_NAME,
                                                                     IP_NAME,
                                                                     {
                                                                         "location": LOCATION,
                                                                         "sku": {"name": "Basic"},
                                                                         "public_ip_allocation_method": "Dynamic",
                                                                         "public_ip_address_version": "IPV4"
                                                                     }
                                                                     )
        ip_address_result = poller.result()
        print("Create Interface")
        poller = network_client.network_interfaces.create_or_update(RESOURCE_GROUP_NAME,
                                                                    NIC_NAME,
                                                                    {
                                                                        "location": LOCATION,
                                                                        "ip_configurations": [{
                                                                            "name": IP_CONFIG_NAME,
                                                                            "subnet": {"id": subnet_result.id},
                                                                            "public_ip_address": {
                                                                                "id": ip_address_result.id}
                                                                        }],
                                                                        "enableAcceleratedNetworking": ACC
                                                                    }
                                                                    )
        nic_result = poller.result()
        print("Create VM")
        poller = compute_client.virtual_machines.create_or_update(RESOURCE_GROUP_NAME, VM_NAME,
                                                                  {
                                                                      "location": LOCATION,
                                                                      "storage_profile": {
                                                                          "osDisk": {
                                                                              "createOption": "fromImage",
                                                                              "diskSizeGB": DISK
                                                                          },
                                                                          "image_reference": images_list[os]
                                                                      },
                                                                      "hardware_profile": {
                                                                          "vm_size": SIZE
                                                                      },
                                                                      "os_profile": {
                                                                          "computer_name": VM_NAME,
                                                                          "admin_username": USERNAME,
                                                                          "admin_password": PASSWORD,
                                                                          "customdata": CUSTOM
                                                                      },
                                                                      "network_profile": {
                                                                          "network_interfaces": [{
                                                                              "id": nic_result.id,
                                                                          }],
                                                                      },
                                                                      "priority": SPOT,
                                                                      "evictionPolicy": DELETE,
                                                                      "billingProfile": {
                                                                          "maxPrice": MAXPRICE
                                                                      }
                                                                  }
                                                                  )
        vm_result = poller.result()
        print("Create VM {} successful".format(tag))
    except:
        print("Create VM {} fail".format(tag))
        delete_vm(subscription_id, credential, tag)
        print("Deleting resource group...")


def start_vm(subscription_id, credential, tag):
    compute_client = ComputeManagementClient(credential, subscription_id)
    GROUP_NAME = tag
    VM_NAME = tag
    async_vm_start = compute_client.virtual_machines.start(
        GROUP_NAME, VM_NAME)
    async_vm_start.wait()


def stop_vm(subscription_id, credential, tag):
    compute_client = ComputeManagementClient(credential, subscription_id)
    GROUP_NAME = tag
    VM_NAME = tag
    async_vm_deallocate = compute_client.virtual_machines.deallocate(
        GROUP_NAME, VM_NAME)
    async_vm_deallocate.wait()


def delete_vm(subscription_id, credential, tag):
    resource_client = ResourceManagementClient(credential, subscription_id)
    GROUP_NAME = tag
    resource_client.resource_groups.delete(GROUP_NAME)


def change_ip(subscription_id, credential, tag):
    compute_client = ComputeManagementClient(credential, subscription_id)
    GROUP_NAME = tag
    VM_NAME = tag
    async_vm_deallocate = compute_client.virtual_machines.deallocate(
        GROUP_NAME, VM_NAME)
    async_vm_deallocate.wait()
    time.sleep(10)
    async_vm_start = compute_client.virtual_machines.start(
        GROUP_NAME, VM_NAME)
    async_vm_start.wait()


def list(subscription_id, credential):
    network_client = NetworkManagementClient(credential, subscription_id)
    info = network_client.public_ip_addresses.list_all()
    compute_client = ComputeManagementClient(credential, subscription_id)
    info2 = compute_client.virtual_machines.list_all()
    iplist = []
    taglist = []
    for info in info:
        info = str(info)
        info = str(info).replace("'", "").replace('"', "")
        info = info.split(", ")[-7].split(" ")[1]
        iplist.append(info)
    for info2 in info2:
        info2 = str(info2)
        info2 = str(info2).replace("'", "").replace('"', "")
        info2 = info2.split(", ")[2].split(" ")[1]
        taglist.append(info2)
    dict = {"ip": iplist, "tag": taglist}
    return dict

