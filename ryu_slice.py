from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu import cfg

from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import arp
from ryu.lib.packet import ether_types



class DirectionSlicing(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(DirectionSlicing, self).__init__(*args, **kwargs)

        CONF = cfg.CONF
        CONF.register_opts([
            cfg.StrOpt('slices_configuration', default='EEE', help = ('Configuration of the slices')),
            cfg.ListOpt('users_configuration', default='', help = ('Json format of user list'))
        ])
        self.slices = CONF.slices_configuration
        self.users = CONF.users_configuration
        self.user_basestations = []
        for i in range(0, len(self.users)-1, 2):
            self.user_basestations.append({'label': self.users[i], 'base_station': self.users[i+1]})

        #print(self.user_basestations)
        #print(self.user_basestations[0])

        #print(self.users)

        #print(self.slices)
        # out_port = slice_to_port[dpid][in_port]
        #self.slice_to_port = {
        #    1: {3: 1, 2: 3, 1: 0},
        #    6: {1: 3, 3: 2, 2: 0},
        #    3: {1: 2, 2: 0},
        #    4: {3: 1, 1: 0, 2: 0, 4: 0},
        #}
        self.slice_to_port = {}
        self.mac_to_port = {}

        #Switches ports configuration
        for i in range(3):
            if self.slices[i] == "E":
                self.slice_to_port[(i+1)] =  {1: 3, 2: 0, 3: 1}
                self.slice_to_port[(i+4)] =  {1: 2, 2: 1, 3: 0, 4: 0}
                self.slice_to_port[(i+7)] =  {1: 0, 2: 0, 3: 0, 4: 5, 5: 4}
                self.slice_to_port[(i+10)] = {1: 2, 2: 1, 3: 0, 4: 0}
                self.slice_to_port[(i+13)] = {1 :2, 2: 1}
                if i > 0 and self.slices[i] == self.slices[i-1]:
                    self.slice_to_port[(i+4)] =  {1 : [2, 3], 2: [1, 3], 4: 0 , 3: [2, 1]}
                    self.slice_to_port[(i+6)] = {1 : [4, 5], 2 : 0, 4: [1, 5], 3: 0, 5: [4, 1]}
                    self.slice_to_port[(i+7)] = {1 : [4, 5], 2 : 0, 4: [1, 5], 3: 0, 5: [4, 1]}
            if self.slices[i] == "M":
                self.slice_to_port[(i+1)] =  {1: 3, 2: 0, 3: 1}
                self.slice_to_port[(i+4)] =  {1: 2, 2: 1, 3: 0, 4: 0}
                self.slice_to_port[(i+7)] =  {1: 0, 2: 0, 3: 4, 4: 3}
                self.slice_to_port[(i+10)] = {1: 2, 2: 1, 3: 0, 4: 0}
                self.slice_to_port[(i+13)] = {1 :0, 2: 3, 3: 2}
                if i > 0 and self.slices[i] == self.slices[i-1]:
                    self.slice_to_port[(i+10)] = {1: [2, 3], 2:[1, 3], 3:[1, 2], 4: 0}
                    self.slice_to_port[(i+12)] = {1: [2, 3], 2: [1, 3], 3: [1, 2]}
                    self.slice_to_port[(i+13)] = {1: [2, 3], 2: [1, 3], 3: [1, 2]}
            if self.slices[i] == "U":
                self.slice_to_port[(i+1)] =  {1: 4, 2: 0, 3: 0, 4: 1}
                self.slice_to_port[(i+4)] =  {1: 2, 2: 1, 3: 0, 4: 0}
                self.slice_to_port[(i+7)] =  {1: 2, 2: 1, 3: 0, 4: 0}
                self.slice_to_port[(i+10)] = {1: 2, 2: 1, 3: 0, 4: 0}
                self.slice_to_port[(i+13)] = {1 :2, 2: 0} 
                if i > 0 and self.slices[i] == self.slices[i-1]:
                    self.slice_to_port[(i)] = {1: [2, 4, 3], 2: [3, 1, 4], 3: [1, 2, 4], 4: [1, 2, 3]}
                    self.slice_to_port[(i+1)] = {1: [2, 4, 3], 2: [3, 1, 4], 3: [1, 2, 4], 4: [1, 2, 3]}
                    self.slice_to_port[(i+4)] =  {1 : 4, 2: 0, 3: 0, 4: 1}
                        
        
        #Base station 1 ports configuration with users
        self.slice_to_port[16] = {}
        users_bs1 = 0
        temp_user_bs1=[]
        for k in self.user_basestations:
            if k.get('base_station') == 'BS1':
                users_bs1 += 1
                temp_user_bs1.append(users_bs1)
                #self.slice_to_port[16][users_bs1] = 2
            else:
                users_bs1 += 0
        if(len(temp_user_bs1) > 1):
            self.slice_to_port[16][users_bs1 + 1] = temp_user_bs1
        else:
            self.slice_to_port[16][users_bs1 + 1] = users_bs1
        if len(temp_user_bs1) > 1:
            for user in temp_user_bs1:
                self.slice_to_port[16][user] = [users_bs1+1]
                for i in range(len(temp_user_bs1)):
                    if temp_user_bs1[i] != user:
                        self.slice_to_port[16][user].append(temp_user_bs1[i])
        else:
            self.slice_to_port[16][temp_user_bs1[0]] = users_bs1+1

        #self.slice_to_port[16] = {1:2, 2:1}
        
        #Base station 2 ports configuration with users
        self.slice_to_port[17] = {}
        users_bs2 = 0
        temp_user_bs2=[]
        for k in self.user_basestations:
            if k.get('base_station') == 'BS2':
                users_bs2 += 1
                temp_user_bs2.append(users_bs2)
                #self.slice_to_port[16][users_bs1] = 2
            else:
                users_bs2 += 0
        if(len(temp_user_bs2) > 1):
            self.slice_to_port[17][users_bs2 + 1] = temp_user_bs2
        else:
            self.slice_to_port[17][users_bs2 + 1] = users_bs2
        if len(temp_user_bs2) > 1:
            for user in temp_user_bs2:
                self.slice_to_port[17][user] = [users_bs2+1]
                for i in range(len(temp_user_bs2)):
                    if temp_user_bs2[i] != user:
                        self.slice_to_port[17][user].append(temp_user_bs2[i])
        else:
            self.slice_to_port[17][temp_user_bs2[0]] = users_bs2+1
        
        #Base station 3 ports configuration with users
        self.slice_to_port[18] = {}
        users_bs3 = 0
        temp_user_bs3=[]
        for k in self.user_basestations:
            if k.get('base_station') == 'BS3':
                users_bs3 += 1
                temp_user_bs3.append(users_bs3)
                #self.slice_to_port[16][users_bs1] = 2
            else:
                users_bs3 += 0
        if(len(temp_user_bs3) > 1):
            self.slice_to_port[18][users_bs3 + 1] = temp_user_bs3
        else:
            self.slice_to_port[18][users_bs3 + 1] = users_bs3
        if len(temp_user_bs3) > 1:
            for user in temp_user_bs3:
                self.slice_to_port[18][user] = [users_bs3+1]
                for i in range(len(temp_user_bs3)):
                    if temp_user_bs3[i] != user:
                        self.slice_to_port[18][user].append(temp_user_bs3[i])
        else:
            self.slice_to_port[18][temp_user_bs3[0]] = users_bs3+1
        #self.slice_to_port[18] = {1:2, 2:1}
        print(self.slice_to_port[16])
        print(self.slice_to_port[17])
        print(self.slice_to_port[18])
    


    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # construct flow_mod message and send it.
        mod = parser.OFPFlowMod(
            datapath=datapath,
            match=match,
            cookie=0,
            command=ofproto.OFPFC_ADD,
            idle_timeout=20,
            hard_timeout=120,
            priority=priority,
            flags=ofproto.OFPFF_SEND_FLOW_REM,
            actions=actions,
        )
        datapath.send_msg(mod)

    def _send_package(self, msg, datapath, in_port, actions):
        data = None
        ofproto = datapath.ofproto
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data,
        )
        #self.logger.info("send_msg %s", out)
        datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        in_port = msg.in_port
        dpid = datapath.id

        pkt = packet.Packet(msg.data)
        pkt_eth = pkt.get_protocol(ethernet.ethernet)
        #pkt_arp = pkt.get_protocol(arp.arp)

    

        if pkt_eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            # self.logger.info("LLDP packet discarded.")
            return

        
        if isinstance(self.slice_to_port[dpid][in_port], list):
            actions = []
            for out_port in self.slice_to_port[dpid][in_port]:
                actions.append(datapath.ofproto_parser.OFPActionOutput(out_port))
            #actions = [datapath.ofproto_parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            match = datapath.ofproto_parser.OFPMatch(in_port=in_port)
            #self.logger.info("INFO sending packet from s%s (out_port=%s)", dpid, out_port)
            self.add_flow(datapath, 2, match, actions)
            self._send_package(msg, datapath, in_port, actions)
            return



        #self.logger.info("INFO packet arrived in s%s (in_port=%s)", dpid, in_port)
        out_port = self.slice_to_port[dpid][in_port]

        if out_port == 0:
            # ignore handshake packet
            # self.logger.info("packet in s%s in_port=%s discarded.", dpid, in_port)
            return
        

        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        match = datapath.ofproto_parser.OFPMatch(in_port=in_port)
        #self.logger.info("INFO sending packet from s%s (out_port=%s)", dpid, out_port)
        self.add_flow(datapath, 2, match, actions)
        self._send_package(msg, datapath, in_port, actions)
