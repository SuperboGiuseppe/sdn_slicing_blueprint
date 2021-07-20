#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink


class Mobile_Infrastructure(Topo):
    #Initialize link types built from https://www.ericsson.com/en/reports-and-papers/white-papers/5g-wireless-access-an-overview
    URLLC_user_plane_link_config = dict(jitter=1)
    mMTC_user_plane_link_config = dict(jitter=1)
    eMBB_user_plane_link_config = dict(jitter=4)
    URLLC_control_plane_link_config = dict(jitter=1)
    mMTC_control_plane_link_config = dict(jitter=1)
    eMBB_control_plane_link_config = dict(jitter=10)
    datacenters = []
    users = []
    
    def __init__(self, datacenters, users):
        #Initialize mininet topology
        Topo.__init__(self)

        self.datacenters = datacenters
        self.users = users
    
    def deploy_slice(self, edge_datacenter, local_datacenter, central_datacenter, slice, users):
        if slice == "URLLC":
            user_plane_link_config = self.URLLC_user_plane_link_config
            control_plane_link_config = self.URLLC_control_plane_link_config
        if slice == "mMTC":
            user_plane_link_config = self.mMTC_user_plane_link_config
            control_plane_link_config = self.mMTC_control_plane_link_config
        if slice == "eMBB":
            user_plane_link_config = self.eMBB_user_plane_link_config
            control_plane_link_config = self.eMBB_control_plane_link_config

        #Deploying edge_datacenter
        self.addSwitch("Edge_Core_Switch")
        for host in edge_datacenter.hosts:
            host_name = "Edge_" + host
            self.addHost(host_name)
            self.addLink(host_name, "Edge_Core_Switch", user_plane_link_config)
        
        #Deploying local_datacenter
        self.addSwitch("Local_Core_Switch")
        for host in local_datacenter.hosts:
            host_name = "Local_" + host
            self.addHost(host_name)
            self.addLink(host_name, "Local_Core_Switch", control_plane_link_config)

        #Deploying central_datacenter
        self.addSwitch("central_Core_Switch")
        for host in central_datacenter.hosts:
            host_name = "Central_" + host
            self.addHost(host_name)
            self.addLink(host_name, "Central_Core_Switch", control_plane_link_config)

        #Connecting slice switches
        self.addLink("Edge_Core_Switch", "Local_Core_Switch", control_plane_link_config)
        self.addLink("Local_Core_Switch", "Central_Core_Switch", control_plane_link_config)

        #Deploying users
        for user in users:
            self.addHost(user)
            self.addLink(user, "Edge_Core_Switch", user_plane_link_config)



class Datacenter:
    def __init__(self, x, y, datacenter_region, hosts_list, datacenter_label):
        self.hosts=hosts_list
        self.position=(x,y)
        self.region = datacenter_region
        self.name = datacenter_label





        






