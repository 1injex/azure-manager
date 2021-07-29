# coding:utf8
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute.models import DiskCreateOption

import time,base64


def create_credential_object(tenant_id, client_id, client_secret):
    print("Create Credential Object")
    tenant_id = tenant_id
    client_id = client_id
    client_secret = client_secret
    credential = ServicePrincipalCredentials(tenant=tenant_id, client_id=client_id, secret=client_secret)
    return credential


def create_resource_group(subscription_id, credential, tag, location):
    print("Create eEsource Group")
    credential = credential
    resource_client = ResourceManagementClient(credential, subscription_id)
    RESOURCE_GROUP_NAME = tag
    LOCATION = location
    rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
                                                                 {
                                                                     "location": LOCATION
                                                                 }
                                                                 )


def create_or_update_vm(subscription_id, credential, tag, location, username, password, size, os,rootpwd):
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
    ROOT_PWD = rootpwd
    SIZE = size
    if os == "ubuntu18":
        publisher = "Canonical"
        offer = "UbuntuServer"
        sku = "18.04-LTS"
        version = "latest"
    elif os == "ubuntu16":
        publisher = "Canonical"
        offer = "UbuntuServer"
        sku = "16.04.0-LTS"
        version = "latest"
    elif os == "centos":
        publisher = "OpenLogic"
        offer = "CentOS"
        sku = "7.5"
        version = "latest"
    elif os == "debian10":
        publisher = "Debian"
        offer = "debian-10"
        sku = "10"
        version = "latest"
    else:
        publisher = "Canonical"
        offer = "UbuntuServer"
        sku = "18.04-LTS"
        version = "latest"


    network_client = NetworkManagementClient(credential, subscription_id)
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
    print("Create IP")
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
    print("Creaate Network Interfaces")
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
                                                                }
                                                                )
    nic_result = poller.result()
    s = "IyEvYmluL2Jhc2gKZWNobyByb290OnBweHdvMTIzIHxzdWRvIGNocGFzc3dkIHJvb3QKc3VkbyBzZWQgLWkgJ3MvXi4qUGVybWl0Um9vdExvZ2luLiovUGVybWl0Um9vdExvZ2luIHllcy9nJyAvZXRjL3NzaC9zc2hkX2NvbmZpZzsKc3VkbyBzZWQgLWkgJ3MvXi4qUGFzc3dvcmRBdXRoZW50aWNhdGlvbi4qL1Bhc3N3b3JkQXV0aGVudGljYXRpb24geWVzL2cnIC9ldGMvc3NoL3NzaGRfY29uZmlnOwpzdWRvIHNlcnZpY2Ugc3NoZCByZXN0YXJ0"
    if (ROOT_PWD != ""):
        d = base64.b64decode(s).decode('latin-1')
        d = d.replace("ppxwo123",ROOT_PWD)
        CUSTOM_DATA = base64.b64encode(b_d.encode("utf-8")).decode('latin-1')
    else:
        CUSTOM_DATA = s
    poller = compute_client.virtual_machines.create_or_update(RESOURCE_GROUP_NAME, VM_NAME,
                                                              {
                                                                  "location": LOCATION,
                                                                  "storage_profile": {
                                                                      "osDisk":{
                                                                          "createOption":"fromImage",
                                                                          "diskSizeGB":64
                                                                      },
                                                                      "image_reference": {
                                                                          "offer": offer,
                                                                          "publisher": publisher,
                                                                          "sku": sku,
                                                                          "version": version
                                                                      }
                                                                  },
                                                                  "hardware_profile": {
                                                                      "vm_size": SIZE
                                                                  },
                                                                  "os_profile": {
                                                                      "computer_name": VM_NAME,
                                                                      "admin_username": USERNAME,
                                                                      "admin_password": PASSWORD,
                                                                      "custom_data": CUSTOM_DATA
                                                                  },
                                                                  "network_profile": {
                                                                      "network_interfaces": [{
                                                                          "id": nic_result.id,
                                                                      }],
                                                                  }
                                                              }
                                                              )
    vm_result = poller.result()
    print(vm_result)


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
