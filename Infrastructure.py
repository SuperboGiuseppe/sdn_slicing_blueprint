#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import Controller
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.link import TCLink

import json



class MobileInfrastructure(Topo):
    def __init__(self, slice_configuration, users):
        #Initialize mininet topology
        Topo.__init__(self)
        self.slices = slice_configuration
        self.users = users


        for i in range(15):
            sconfig = {"dpid": "%016x" % (i+1)}
            self.addSwitch("Switch%d" % (i+1), protocols="OpenFlow10", **sconfig)
        
        for i in range(3):
            sconfig = {"dpid": "%016x" % (i+15+1)}
            self.addSwitch("BS%d" % (i+1), protocols="OpenFlow10", **sconfig)
        
        for i in range(3):
            self.addHost("Probe%d" % (i+1))

        self.slice_configuration()
    
    def slice_configuration(self):
        #Initialize link types built from https://www.ericsson.com/en/reports-and-papers/white-papers/5g-wireless-access-an-overview
        base_station_link_config = dict(bw=20, delay="2ms")

        URLLC_user_plane_link_config = dict(bw=20, delay="2ms")
        URLLC_control_plane_link_config = dict(bw=20, delay="10ms")

        mMTC_user_plane_link_config = dict(bw=20, delay="2ms")
        mMTC_control_plane_link_config = dict(bw=20, delay="10ms")
        
        eMBB_user_plane_link_config = dict(bw=20, delay="5ms")
        eMBB_control_plane_link_config = dict(bw=20, delay="10ms")

        data_center_link_config = dict(bw=100, delay="1ms")
       
        
        
        #access_network_config = dict(delay=7, bw=30)


        users_bs1 = 0
        users_bs2 = 0
        users_bs3 = 0


        for k in self.users:
            if k.get('base_station') == 'BS1':
                users_bs1 += 1
                self.addHost(k.get("label"))
                self.addLink(k.get("label"), 'BS1', 1, users_bs1, delay='1ms')
            if k.get('base_station') == 'BS2':
                users_bs2 += 1
                self.addHost(k.get("label"))
                self.addLink(k.get("label"), 'BS2', 1, users_bs2, delay='1ms')
            if k.get('base_station') == 'BS3':
                users_bs3 += 1
                self.addHost(k.get("label"))
                self.addLink(k.get("label"), 'BS3', 1, users_bs3, delay='1ms')
        """   
        for k in self.users:
            if k.get('base_station') == 'BS1':
                temp_bs1 += 1
                self.addLink(k.get("label"), 'BS1', temp_bs1, users_bs1+1, delay='1ms')
            if k.get('base_station') == 'BS2':
                temp_bs2 += 1
                self.addLink(k.get("label"), 'BS2', temp_bs2, users_bs2+1, delay='1ms')
            if k.get('base_station') == 'BS3':
                temp_bs3 += 1
                self.addLink(k.get("label"), 'BS3', temp_bs3, users_bs3+1, delay='1ms')

        
        print(user_bs)
        """
        user_bs = [users_bs1, users_bs2, users_bs3]
        #Switch links configuration
        for i in range(3):
            if self.slices[i] == "E":
                self.addLink("BS"+str(i+1), "Switch"+str(i+1), user_bs[i]+1, 1, **eMBB_user_plane_link_config)
                self.addLink("Switch"+str(i+1), "Switch"+str(i+4), 3, 1, **eMBB_user_plane_link_config)
                self.addLink("Switch"+str(i+4), "Switch"+str(i+7), 2, 4, **eMBB_user_plane_link_config)
                self.addLink("Switch"+str(i+7), "Switch"+str(i+10), 3, 1, **eMBB_control_plane_link_config)
                self.addLink("Switch"+str(i+10), "Switch"+str(i+13), 2, 2, **eMBB_control_plane_link_config)
                self.addLink("Switch"+str(i+7), "Probe"+str(i+1), 5, 1, **data_center_link_config)
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
                self.addLink("BS"+str(i+1), "Switch"+str(i+1), user_bs[i]+1, 1, **mMTC_user_plane_link_config)
                self.addLink("Switch"+str(i+1), "Switch"+str(i+4), 3, 1, **mMTC_user_plane_link_config)
                self.addLink("Switch"+str(i+4), "Switch"+str(i+7), 2, 4, **mMTC_user_plane_link_config)
                self.addLink("Switch"+str(i+7), "Switch"+str(i+10), 3, 1, **mMTC_user_plane_link_config)
                self.addLink("Switch"+str(i+10), "Switch"+str(i+13), 2, 2,  **mMTC_user_plane_link_config)
                self.addLink("Switch"+str(i+13), "Probe"+str(i+1), 3, 1, **data_center_link_config)
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
                self.addLink("BS"+str(i+1), "Switch"+str(i+1), user_bs[i]+1, 1, **URLLC_user_plane_link_config)
                self.addLink("Switch"+str(i+1), "Switch"+str(i+4), 3, 1, **URLLC_control_plane_link_config)
                self.addLink("Switch"+str(i+4), "Switch"+str(i+7), 2, 4, **URLLC_control_plane_link_config)
                self.addLink("Switch"+str(i+7), "Switch"+str(i+10), 3, 1, **URLLC_control_plane_link_config)
                self.addLink("Switch"+str(i+10), "Switch"+str(i+13), 2, 2, **URLLC_control_plane_link_config)
                self.addLink("Switch"+str(i+1), "Probe"+str(i+1), 4, 1, **data_center_link_config)
                if i > 0: 
                    if self.slices[i] == self.slices[i-1]:
                        self.addLink("Switch"+str(i+4), "Switch"+str(i), 4, 2, **URLLC_user_plane_link_config)
                        self.addLink("Switch"+str(i+4), "Switch"+str(i+6), 3, 1, **URLLC_control_plane_link_config)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+6), 4, 2, **URLLC_control_plane_link_config)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+12), 3, 1, **URLLC_control_plane_link_config)
                    else:
                        self.addLink("Switch"+str(i+4), "Switch"+str(i), 4, 2)
                        self.addLink("Switch"+str(i+4), "Switch"+str(i+6), 3, 1)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+6), 4, 2)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+12), 3, 1)
           
        
        """
        for i in range(0, len(self.users), 2):
            self.addHost(self.users[i])
            self.addLink(self.users[i], self.users[i+1], i, (len(self.users)/2)+1 , delay='1ms')
        """
def reading_configuration(file_path):
    with open (file_path, "r") as file:
        conf_data = file.readlines()

    user_base_station_configuration = []
    for string in conf_data[5].split('\"')[0].split(' = ')[1].split(', '):
        user_base_station_configuration.append(string)
    user_basestations = []
    for i in range(0, len(user_base_station_configuration)-1, 2):
        user_basestations.append({'label': user_base_station_configuration[i], 'base_station': user_base_station_configuration[i+1]})

    return conf_data[4].split("\"")[1], user_basestations

def main():
    #E = eMBB, M= mMTC, U = URLLC
    slice_configuration, users = reading_configuration("/home/vagrant/params.conf")
    print(slice_configuration)
    users[len(users)-1]["base_station"] = users[len(users)-1]["base_station"].rstrip("\n")
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