#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import Controller
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.link import TCLink





class MobileInfrastructure(Topo):
    def __init__(self, slice_configuration, users):
        #Initialize mininet topology
        Topo.__init__(self)
        self.slices = slice_configuration
        self.users = users


        for i in range(15):
            sconfig = {"dpid": "%016x" % (i+1)}
            self.addSwitch("Switch%d" % (i+1), protocols="OpenFlow13", **sconfig)
        
        for i in range(3):
            sconfig = {"dpid": "%016x" % (i+15+1)}
            self.addSwitch("BS%d" % (i+1), protocols="OpenFlow13", **sconfig)
        
        for i in range(3):
            self.addHost("Probe%d" % (i+1))

        self.slice_configuration()
    
    def slice_configuration(self):
        #Initialize link types built from https://www.ericsson.com/en/reports-and-papers/white-papers/5g-wireless-access-an-overview
        URLLC_user_plane_link_config = dict(delay=1, bw=10)
        mMTC_user_plane_link_config = dict(delay=1, bw=20)
        eMBB_user_plane_link_config = dict(delay=4, bw=30)
        URLLC_control_plane_link_config = dict(delay=1, bw=10)
        #mMTC_control_plane_link_config = dict(delay=1)
        eMBB_control_plane_link_config = dict(delay=10, bw=30)
        #access_network_config = dict(delay=7, bw=30)


        #Switch links configuration
        for i in range(3):
            if self.slices[i] == "E":
                self.addLink("BS"+str(i+1), "Switch"+str(i+1), 2, 1, **eMBB_user_plane_link_config)
                self.addLink("Switch"+str(i+1), "Switch"+str(i+4), 3, 1, **eMBB_user_plane_link_config)
                self.addLink("Switch"+str(i+4), "Switch"+str(i+7), 2, 4, **eMBB_user_plane_link_config)
                self.addLink("Switch"+str(i+7), "Switch"+str(i+10), 3, 1, **eMBB_control_plane_link_config)
                self.addLink("Switch"+str(i+10), "Switch"+str(i+13), 2, 2, **eMBB_control_plane_link_config)
                self.addLink("Switch"+str(i+7), "Probe"+str(i+1), 5, 1, **eMBB_user_plane_link_config)
                if i > 0:
                    if self.slices[i] == self.slices[i-1]:
                        self.addLink("Switch"+str(i+4), "Switch"+str(i), 4, 2, **eMBB_user_plane_link_config)
                        self.addLink("Switch"+str(i+4), "Switch"+str(i+6), 3, 1, **eMBB_user_plane_link_config)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+6), 4, 2, **eMBB_control_plane_link_config)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+12), 3, 1,**eMBB_control_plane_link_config)
                    else:
                        self.addLink("Switch"+str(i+4), "Switch"+str(i), 4, 2)
                        self.addLink("Switch"+str(i+4), "Switch"+str(i+6), 3, 1)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+6), 4, 2)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+12), 3, 1)
            if self.slices[i] == "M":
                self.addLink("BS"+str(i+1), "Switch"+str(i+1), 2, 1, **mMTC_user_plane_link_config)
                self.addLink("Switch"+str(i+1), "Switch"+str(i+4), 3, 1, **mMTC_user_plane_link_config)
                self.addLink("Switch"+str(i+4), "Switch"+str(i+7), 2, 4, **mMTC_user_plane_link_config)
                self.addLink("Switch"+str(i+7), "Switch"+str(i+10), 3, 1, **mMTC_user_plane_link_config)
                self.addLink("Switch"+str(i+10), "Switch"+str(i+13), 2, 2,  **mMTC_user_plane_link_config)
                self.addLink("Switch"+str(i+13), "Probe"+str(i+1), 3, 1, **mMTC_user_plane_link_config)
                if i > 0:
                    if self.slices[i] == self.slices[i-1]:
                        self.addLink("Switch"+str(i+4), "Switch"+str(i), 4, 2, **mMTC_user_plane_link_config)
                        self.addLink("Switch"+str(i+4), "Switch"+str(i+6), 3, 1, **mMTC_user_plane_link_config)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+6), 4, 2, **mMTC_user_plane_link_config)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+12), 3, 1, **mMTC_user_plane_link_config)
                    else:
                        self.addLink("Switch"+str(i+4), "Switch"+str(i), 4, 2)
                        self.addLink("Switch"+str(i+4), "Switch"+str(i+6), 3, 1)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+6), 4, 2)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+12), 3, 1)
            if self.slices[i] == "U":
                self.addLink("BS"+str(i+1), "Switch"+str(i+1), 2, 1, **URLLC_user_plane_link_config)
                self.addLink("Switch"+str(i+1), "Switch"+str(i+4), 3, 1, **URLLC_user_plane_link_config)
                self.addLink("Switch"+str(i+4), "Switch"+str(i+7), 2, 4, **URLLC_user_plane_link_config)
                self.addLink("Switch"+str(i+7), "Switch"+str(i+10), 3, 1, **URLLC_user_plane_link_config)
                self.addLink("Switch"+str(i+10), "Switch"+str(i+13), 2, 2, **URLLC_control_plane_link_config)
                self.addLink("Switch"+str(i+1), "Probe"+str(i+1), 4, 1)
                if i > 0: 
                    if self.slices[i] == self.slices[i-1]:
                        self.addLink("Switch"+str(i+4), "Switch"+str(i), 4, 2, **URLLC_user_plane_link_config)
                        self.addLink("Switch"+str(i+4), "Switch"+str(i+6), 3, 1, **URLLC_user_plane_link_config)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+6), 4, 2, **URLLC_user_plane_link_config)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+12), 3, 1, **URLLC_control_plane_link_config)
                    else:
                        self.addLink("Switch"+str(i+4), "Switch"+str(i), 4, 2)
                        self.addLink("Switch"+str(i+4), "Switch"+str(i+6), 3, 1)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+6), 4, 2)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+12), 3, 1)
            
        for user in self.users:
            self.addHost(user["label"])
            self.addLink(user["label"], user["base_station"], 1, 1)

def reading_configuration(file_path):
    with open (file_path, "r") as file:
        conf_data = file.readlines()
    
    return conf_data[4].split("\"")[1]

def main():
    users = [{"label":"user1", "base_station":"BS1"}, {"label":"user2", "base_station":"BS2"}, {"label":"user3", "base_station":"BS3"}]
    #E = eMBB, M= mMTC, U = URLLC
    slice_configuration = reading_configuration("/home/vagrant/params.conf")
    topology = MobileInfrastructure(slice_configuration, users)
    net = Mininet(
        topo=topology,
        switch=OVSKernelSwitch,
        build=False,
        autoSetMacs=True,
        autoStaticArp=True,
        link=TCLink,
    )
    controller = RemoteController("c1", ip="127.0.0.1", port=6633)
    net.addController(controller)
    net.start()
    CLI(net)
    net.stop()

main()