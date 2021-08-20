#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import Controller



class MobileInfrastructure(Topo):
    def __init__(self, slice_configuration, users):
        #Initialize mininet topology
        Topo.__init__(self)
        self.slices = slice_configuration
        self.users = users


        for i in range(15):
            sconfig = {"dpid": "%016x" % (i+1)}
            self.addSwitch("Switch%d" % (i+1), **sconfig)
        
        for i in range(3):
            self.addSwitch("BS%d" % (i+1))
        
        for i in range(3):
            self.addHost("Probe%d" % (i+1))

        self.slice_configuration()
    
    def slice_configuration(self):
        #Initialize link types built from https://www.ericsson.com/en/reports-and-papers/white-papers/5g-wireless-access-an-overview
        URLLC_user_plane_link_config = dict(jitter=1, bw=10)
        mMTC_user_plane_link_config = dict(jitter=1, bw=20)
        eMBB_user_plane_link_config = dict(jitter=4, bw=30)
        URLLC_control_plane_link_config = dict(jitter=1, bw=10)
        mMTC_control_plane_link_config = dict(jitter=1)
        eMBB_control_plane_link_config = dict(jitter=10, bw=30)

        #Switch links configuration
        for i in range(3):
            if self.slices[i] == "E":
                self.addLink("BS"+str(i+1), "Switch"+str(i+1), **eMBB_user_plane_link_config)
                self.addLink("Switch"+str(i+1), "Switch"+str(i+4), **eMBB_user_plane_link_config)
                self.addLink("Switch"+str(i+4), "Switch"+str(i+7), **eMBB_user_plane_link_config)
                self.addLink("Switch"+str(i+7), "Switch"+str(i+10), **eMBB_control_plane_link_config)
                self.addLink("Switch"+str(i+10), "Switch"+str(i+13), **eMBB_control_plane_link_config)
                self.addLink("Switch"+str(i+13), "Probe"+str(i+1))
                if i > 0:
                    if self.slices[i] == self.slices[i-1]:
                        self.addLink("Switch"+str(i+4), "Switch"+str(i), **eMBB_user_plane_link_config)
                        self.addLink("Switch"+str(i+4), "Switch"+str(i+6), **eMBB_user_plane_link_config)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+6), **eMBB_control_plane_link_config)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+12), **eMBB_control_plane_link_config)
                    else:
                        self.addLink("Switch"+str(i+4), "Switch"+str(i))
                        self.addLink("Switch"+str(i+4), "Switch"+str(i+6))
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+6))
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+12))
            if self.slices[i] == "M":
                self.addLink("BS"+str(i+1), "Switch"+str(i+1), **mMTC_user_plane_link_config)
                self.addLink("Switch"+str(i+1), "Switch"+str(i+4), **mMTC_user_plane_link_config)
                self.addLink("Switch"+str(i+4), "Switch"+str(i+7), **mMTC_user_plane_link_config)
                self.addLink("Switch"+str(i+7), "Switch"+str(i+10), **mMTC_user_plane_link_config)
                self.addLink("Switch"+str(i+10), "Switch"+str(i+13), **mMTC_user_plane_link_config)
                self.addLink("Switch"+str(i+13), "Probe"+str(i+1))
                if i > 0:
                    if self.slices[i] == self.slices[i-1]:
                        self.addLink("Switch"+str(i+4), "Switch"+str(i), **mMTC_user_plane_link_config)
                        self.addLink("Switch"+str(i+4), "Switch"+str(i+6), **mMTC_user_plane_link_config)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+6), **mMTC_user_plane_link_config)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+12), **mMTC_user_plane_link_config)
                    else:
                        self.addLink("Switch"+str(i+4), "Switch"+str(i))
                        self.addLink("Switch"+str(i+4), "Switch"+str(i+6))
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+6))
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+12))
            if self.slices[i] == "U":
                self.addLink("BS"+str(i+1), "Switch"+str(i+1), **URLLC_user_plane_link_config)
                self.addLink("Switch"+str(i+1), "Switch"+str(i+4), **URLLC_user_plane_link_config)
                self.addLink("Switch"+str(i+4), "Switch"+str(i+7), **URLLC_user_plane_link_config)
                self.addLink("Switch"+str(i+7), "Switch"+str(i+10), **URLLC_user_plane_link_config)
                self.addLink("Switch"+str(i+10), "Switch"+str(i+13), **URLLC_control_plane_link_config)
                self.addLink("Switch"+str(i+13), "Probe"+str(i+1))
                if i > 0: 
                    if self.slices[i] == self.slices[i-1]:
                        self.addLink("Switch"+str(i+4), "Switch"+str(i), **URLLC_user_plane_link_config)
                        self.addLink("Switch"+str(i+4), "Switch"+str(i+6), **URLLC_user_plane_link_config)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+6), **URLLC_user_plane_link_config)
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+12), **URLLC_control_plane_link_config)
                    else:
                        self.addLink("Switch"+str(i+4), "Switch"+str(i))
                        self.addLink("Switch"+str(i+4), "Switch"+str(i+6))
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+6))
                        self.addLink("Switch"+str(i+10), "Switch"+str(i+12))
            
        for user in self.users:
            self.addHost(user["label"])
            self.addLink(user["label"], user["base_station"])
        

def main():
    users = [{"label":"user1", "base_station":"BS1"}, {"label":"user2", "base_station":"BS2"}]
    #E = eMBB, M= mMTC, U = URLLC
    slice_configuration = ["E", "M", "U"]
    topology = MobileInfrastructure(slice_configuration, users)
    net = Mininet(topo=topology, controller=None)
    net.start()
    CLI(net)
    net.stop()

main()