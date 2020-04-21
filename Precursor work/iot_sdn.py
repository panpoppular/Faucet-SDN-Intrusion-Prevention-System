# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
An OpenFlow 1.0 L2 learning switch implementation.
"""


from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import tcp
from ryu.lib.packet import ipv4
from ryu.lib.packet import icmp
from ryu.lib import pcaplib
from collections import defaultdict
from collections import deque

class SimpleSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

        #dicts to store packet count by ip address
        self.packet_ratio = defaultdict(lambda: defaultdict(int))
        self.telnet_attempts = defaultdict()

        self.pcap_writer = pcaplib.Writer(open('mypcap.pcap', 'wb'))

        #packet count for evaluation
        # self.true_dropped_count = 0
        # self.false_dropped_count = 0
        # self.bad_count = 0
        # self.good_count = 0

    def add_flow(self, datapath, in_port, dst, src, actions):
        ofproto = datapath.ofproto

        match = datapath.ofproto_parser.OFPMatch(
            in_port=in_port,
            dl_dst=haddr_to_bin(dst), dl_src=haddr_to_bin(src))

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=ofproto.OFP_DEFAULT_PRIORITY,
            flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions)
        datapath.send_msg(mod)

    def block_ip(self, datapath, ip):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch(ipv4_src=ip)

        instructions = [parser.OFPInstructionActions(proto.OFPIT_CLEAR_ACTIONS, [])]

        mod = parser.OFPFlowMod(
                datapath=datapath, match=match, cookie=0,
                command=1, flags=ofproto.OFPFF_SEND_FLOW_REM,
                instructions=instructions)
        
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto

        self.pcap_writer.write_pkt(ev.msg.data)

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src
        
        pkt_tcp = pkt.get_protocol(tcp.tcp)
        print pkt_tcp

        pkt_ipv4 = pkt.get_protocol(ipv4.ipv4)
        print pkt_ipv4

        if pkt_ipv4:
            # print self.true_dropped_count
            # print self.false_dropped_count
            # print self.bad_count
            # print self.good_count
            # print self.telnet_attempts

            #denial of service protection
            self.packet_ratio[pkt_ipv4.src][pkt_ipv4.dst] += 1
            self.logger.info('Packet ratio = %s:%s', self.packet_ratio[pkt_ipv4.src][pkt_ipv4.dst], self.packet_ratio[pkt_ipv4.dst][pkt_ipv4.src])
            
            # if pkt_ipv4.src == '52.221.238.129':
            #     self.bad_count += 1
            # else:
            #     self.good_count += 1
            
            #divisor cannot be zero
            if (self.packet_ratio[pkt_ipv4.dst][pkt_ipv4.src] == 0):
                if(self.packet_ration[pkt_ipv4.src][pkt_ipv4.dst] > 100):
                    return

            elif (self.packet_ratio[pkt_ipv4.src][pkt_ipv4.dst])/(self.packet_ratio[pkt_ipv4.dst][pkt_ipv4.src]) > 8:
                self.logger.info('DOS DROPPED')
                # if pkt_ipv4.src == '52.221.238.129':
                #     self.true_dropped_count += 1
                # else:
                #     self.false_dropped_count += 1

                # self.block_ip(datapath=datapath, ip=pkt_ipv4.src)
                return

            #telnet bruteforce protection
            if pkt_ipv4.proto == 6: # 6 == tcp
                if pkt_tcp.dst_port == 23 and pkt_tcp.has_flags(tcp.TCP_SYN):
                    if not self.telnet_attempts.get(pkt_ipv4.src):
                        self.telnet_attempts[pkt_ipv4.src] = deque()
                    self.telnet_attempts[pkt_ipv4.src].append(time.time())
                    self.logger.info(self.telnet_attempts[pkt_ipv4.src])
                    while len(self.telnet_attempts[pkt_ipv4.src]) > 0 and time.time() - self.telnet_attempts[pkt_ipv4.src][0] > 1:
                        self.telnet_attempts[pkt_ipv4.src].popleft()
                    if len(self.telnet_attempts[pkt_ipv4.src]) > 10:
                        self.logger.info('TELNET DROPPED')
                        # self.true_dropped_count += 1
                        return

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        if not pkt_tcp:
            self.logger.info("packet in %s %s %s %s", dpid, src, dst, msg.in_port)
        else:
            dst_port = pkt_tcp.dst_port
            src_port = pkt_tcp.src_port
            seq = pkt_tcp.seq

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = msg.in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        #if out_port != ofproto.OFPP_FLOOD:
        #    self.add_flow(datapath, msg.in_port, dst, src, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=actions, data=data)
        datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        msg = ev.msg
        reason = msg.reason
        port_no = msg.desc.port_no

        ofproto = msg.datapath.ofproto
        if reason == ofproto.OFPPR_ADD:
            self.logger.info("port added %s", port_no)
        elif reason == ofproto.OFPPR_DELETE:
            self.logger.info("port deleted %s", port_no)
        elif reason == ofproto.OFPPR_MODIFY:
            self.logger.info("port modified %s", port_no)
        else:
            self.logger.info("Illeagal port state %s %s", port_no, reason)
