#!/usr/bin/env python3
"""
SDN Controller for Dynamic Policy-Based Micro-Segmentation

This Ryu controller implements:
1. Traffic monitoring and dependency discovery
2. Role-based policy enforcement  
3. Dynamic OpenFlow rule installation
4. Security violation logging

Key Features:
- Automatic application dependency mapping
- Least-privilege access control
- Real-time policy enforcement
- Attack detection and blocking
"""

import json
import logging
from collections import defaultdict
from datetime import datetime

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp, arp, icmp
from ryu.lib.packet import ether_types

class MicroSegmentationController(app_manager.RyuApp):
    """
    Main SDN controller class for micro-segmentation
    """
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(MicroSegmentationController, self).__init__(*args, **kwargs)
        
        # Initialize data structures
        self.mac_to_port = {}  # MAC address to switch port mapping
        self.ip_to_mac = {}    # IP to MAC address mapping
        self.traffic_flows = defaultdict(int)  # Traffic flow counters
        self.dependency_graph = defaultdict(set)  # Application dependencies
        self.policy_violations = []  # Security violations log
        self.active_connections = set()  # Track active connections for return traffic
        
        # Load role-based policies
        self.load_policies()
        
        # Setup logging
        self.setup_logging()
        
        self.logger.info("Micro-Segmentation Controller Started")
        self.logger.info(f"Loaded {len(self.roles)} roles and {len(self.server_flows)} server flows")

    def setup_logging(self):
        """Configure logging for security events"""
        # Create security events log file
        self.security_log_file = 'security_events.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.security_log_file),
                logging.StreamHandler()
            ]
        )
        
        # Also create a separate security events handler
        self.security_logger = logging.getLogger('security_events')
        security_handler = logging.FileHandler(self.security_log_file)
        security_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.security_logger.addHandler(security_handler)
        
    def load_policies(self):
        """Load role definitions and policies from JSON file"""
        try:
            with open('roles.json', 'r') as f:
                policy_data = json.load(f)
                
            self.roles = policy_data.get('roles', {})
            self.server_flows = policy_data.get('server_dependencies', {}).get('allowed_flows', [])
            
            # Create quick lookup dictionaries
            self.ip_to_role = {}
            self.allowed_connections = set()
            
            # Map IPs to roles
            for role_name, role_data in self.roles.items():
                for host_ip in role_data['hosts']:
                    self.ip_to_role[host_ip] = role_name
                    
                # Build allowed connections set
                for access in role_data['allowed_access']:
                    connection = (host_ip, access['destination'], access['port'])
                    self.allowed_connections.add(connection)
            
            # Add server-to-server flows
            for flow in self.server_flows:
                connection = (flow['source'], flow['destination'], flow['port'])
                self.allowed_connections.add(connection)
                
        except FileNotFoundError:
            self.logger.error("roles.json not found! Using default empty policies.")
            self.roles = {}
            self.server_flows = []
            self.ip_to_role = {}
            self.allowed_connections = set()

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """Handle switch connection and install default flow"""
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        self.logger.info(f"Switch connected: {datapath.id}")
        
        # Install default flow to send packets to controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                        ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        
        # Install ARP handling flow (higher priority)
        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_ARP)
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                        ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 1000, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None, idle_timeout=0):
        """Install a flow rule on the switch"""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                  priority=priority, match=match,
                                  instructions=inst, idle_timeout=idle_timeout)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                  match=match, instructions=inst, 
                                  idle_timeout=idle_timeout)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """Handle incoming packets and apply policies"""
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        
        # Parse packet
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocols(ethernet.ethernet)[0]
        
        if eth_pkt.ethertype == ether_types.ETH_TYPE_LLDP:
            return  # Ignore LLDP packets
            
        dst_mac = eth_pkt.dst
        src_mac = eth_pkt.src
        
        # Learn MAC addresses
        self.mac_to_port[src_mac] = in_port
        
        # Handle ARP packets
        if eth_pkt.ethertype == ether_types.ETH_TYPE_ARP:
            self.handle_arp(datapath, pkt, eth_pkt, in_port)
            return
            
        # Handle IP packets
        if eth_pkt.ethertype == ether_types.ETH_TYPE_IP:
            ip_pkt = pkt.get_protocol(ipv4.ipv4)
            if ip_pkt:
                self.handle_ip_packet(datapath, pkt, eth_pkt, ip_pkt, in_port)
                return
        
        # Default forwarding for other packets
        self.flood_packet(datapath, msg, in_port)

    def handle_arp(self, datapath, pkt, eth_pkt, in_port):
        """Handle ARP packets for IP-MAC learning"""
        arp_pkt = pkt.get_protocol(arp.arp)
        if arp_pkt:
            # Learn IP to MAC mapping
            self.ip_to_mac[arp_pkt.src_ip] = arp_pkt.src_mac
            self.logger.debug(f"Learned: {arp_pkt.src_ip} -> {arp_pkt.src_mac}")
            
        # Flood ARP packets
        self.flood_packet(datapath, datapath.ofproto_parser.OFPPacketIn(
            buffer_id=datapath.ofproto.OFP_NO_BUFFER,
            data=pkt.data
        ), in_port)

    def handle_ip_packet(self, datapath, pkt, eth_pkt, ip_pkt, in_port):
        """Handle IP packets and apply security policies"""
        src_ip = ip_pkt.src
        dst_ip = ip_pkt.dst
        
        # Learn IP to MAC mapping
        self.ip_to_mac[src_ip] = eth_pkt.src
        
        # Extract port information for TCP/UDP
        dst_port = None
        protocol = None
        
        tcp_pkt = pkt.get_protocol(tcp.tcp)
        udp_pkt = pkt.get_protocol(udp.udp)
        
        if tcp_pkt:
            dst_port = tcp_pkt.dst_port
            protocol = 'tcp'
        elif udp_pkt:
            dst_port = udp_pkt.dst_port  
            protocol = 'udp'
        else:
            # Handle ICMP and other protocols
            if ip_pkt.proto == 1:  # ICMP
                dst_port = 0  # ICMP doesn't have ports
                protocol = 'icmp'
            else:
                # Allow other protocols (like ARP responses)
                self.forward_packet(datapath, pkt, eth_pkt, in_port)
                return
            
        # Log traffic flow
        flow_key = f"{src_ip}:{dst_ip}:{dst_port}"
        self.traffic_flows[flow_key] += 1
        
        # Update dependency graph
        if dst_port:
            self.dependency_graph[src_ip].add((dst_ip, dst_port))
            
        self.logger.debug(f"Traffic: {src_ip} -> {dst_ip}:{dst_port} ({protocol})")
        
        # Debug logging
        self.logger.debug(f"Processing packet: {src_ip} -> {dst_ip}:{dst_port} ({protocol})")
        
        # Apply security policy
        if self.is_connection_allowed(src_ip, dst_ip, dst_port):
            self.logger.info(f"ALLOWED: {src_ip} -> {dst_ip}:{dst_port} ({protocol})")
            
            # Log to security events file
            self.log_security_event("ALLOWED", src_ip, dst_ip, dst_port, protocol)
            
            # Track the connection for return traffic
            self.active_connections.add((src_ip, dst_ip, dst_port))
            
            self.forward_packet(datapath, pkt, eth_pkt, in_port)
            self.install_flow_rule(datapath, src_ip, dst_ip, dst_port, protocol, in_port)
            
            # Install return flow rule for all protocols
            self.install_return_flow_rule(datapath, src_ip, dst_ip, dst_port, protocol)
        else:
            self.logger.warning(f"BLOCKED: {src_ip} -> {dst_ip}:{dst_port} ({protocol})")
            
            # Log to security events file
            self.log_security_event("BLOCKED", src_ip, dst_ip, dst_port, protocol)
            
            self.log_security_violation(src_ip, dst_ip, dst_port, protocol)
            # Drop packet (do nothing)

    def is_connection_allowed(self, src_ip, dst_ip, dst_port):
        """Check if connection is allowed by policy"""
        # Special handling for ICMP (ping)
        if dst_port == 0:  # ICMP traffic
            # Temporarily allow all ICMP for debugging
            # return True  # Uncomment this line to allow all ping for testing
            return self.is_icmp_allowed(src_ip, dst_ip)
        
        # Check role-based access (forward direction)
        connection = (src_ip, dst_ip, dst_port)
        if connection in self.allowed_connections:
            return True
        
        # Check if it's return traffic (reverse direction)
        # Allow return traffic for established connections
        if self.is_return_traffic_allowed(src_ip, dst_ip, dst_port):
            return True
            
        # Check if it's a server-to-server communication
        for flow in self.server_flows:
            if (flow['source'] == src_ip and 
                flow['destination'] == dst_ip and 
                flow['port'] == dst_port):
                return True
        
        # Block user-to-user communication (enhanced security)
        user_ips = ["10.0.0.100", "10.0.0.200"]  # HR and Admin
        if src_ip in user_ips and dst_ip in user_ips:
            self.logger.warning(f"BLOCKED: User-to-user communication {src_ip} -> {dst_ip}")
            return False
                
        return False
    
    def is_icmp_allowed(self, src_ip, dst_ip):
        """Check if ICMP (ping) is allowed based on role policies"""
        # Get source role
        src_role = self.ip_to_role.get(src_ip, 'UNKNOWN')
        
        self.logger.debug(f"ICMP check: {src_ip} ({src_role}) -> {dst_ip}")
        
        # HR users (10.0.0.100) can only ping web server (10.0.0.10)
        if src_ip == "10.0.0.100":  # HR user
            if dst_ip == "10.0.0.10":  # Web server
                self.logger.debug("ICMP ALLOWED: HR user to Web server")
                return True
            else:
                self.logger.debug(f"ICMP BLOCKED: HR user to {dst_ip}")
                return False
        
        # Admin users (10.0.0.200) can ping all servers
        elif src_ip == "10.0.0.200":  # Admin user
            server_ips = ["10.0.0.10", "10.0.0.20", "10.0.0.30"]
            if dst_ip in server_ips:
                self.logger.debug(f"ICMP ALLOWED: Admin user to server {dst_ip}")
                return True
            else:
                self.logger.debug(f"ICMP BLOCKED: Admin user to non-server {dst_ip}")
                return False
        
        # Server-to-server ICMP (for network diagnostics)
        server_ips = ["10.0.0.10", "10.0.0.20", "10.0.0.30"]
        if src_ip in server_ips and dst_ip in server_ips:
            self.logger.debug(f"ICMP ALLOWED: Server-to-server {src_ip} -> {dst_ip}")
            return True
        
        # ICMP replies (return traffic)
        if src_ip in server_ips and dst_ip in ["10.0.0.100", "10.0.0.200"]:
            self.logger.debug(f"ICMP ALLOWED: Server reply {src_ip} -> {dst_ip}")
            return True
        
        # Default deny for unknown sources
        self.logger.debug(f"ICMP BLOCKED: Default deny {src_ip} -> {dst_ip}")
        return False
    
    def is_return_traffic_allowed(self, src_ip, dst_ip, dst_port):
        """Check if this is allowed return traffic (response to a legitimate request)"""
        # Server IPs
        server_ips = ["10.0.0.10", "10.0.0.20", "10.0.0.30"]
        user_ips = ["10.0.0.100", "10.0.0.200"]
        
        # If source is a server and destination is a user
        if src_ip in server_ips and dst_ip in user_ips:
            # Check if the reverse connection (user -> server) is allowed
            # Look for allowed connections where user can reach this server
            for allowed_src, allowed_dst, allowed_port in self.allowed_connections:
                if allowed_src == dst_ip and allowed_dst == src_ip:
                    # This is return traffic for an allowed connection
                    self.logger.debug(f"Allowing return traffic: {src_ip} -> {dst_ip}:{dst_port}")
                    return True
        
        # If source is a server and destination is another server (return traffic)
        if src_ip in server_ips and dst_ip in server_ips:
            # Check if reverse server-to-server flow exists
            for flow in self.server_flows:
                if flow['destination'] == src_ip and flow['source'] == dst_ip:
                    self.logger.debug(f"Allowing server return traffic: {src_ip} -> {dst_ip}:{dst_port}")
                    return True
        
        return False

    def forward_packet(self, datapath, pkt, eth_pkt, in_port):
        """Forward packet to destination"""
        dst_mac = eth_pkt.dst
        
        if dst_mac in self.mac_to_port:
            out_port = self.mac_to_port[dst_mac]
        else:
            out_port = datapath.ofproto.OFPP_FLOOD
            
        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        
        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=datapath.ofproto.OFP_NO_BUFFER,
            in_port=in_port,
            actions=actions,
            data=pkt.data
        )
        datapath.send_msg(out)

    def flood_packet(self, datapath, msg, in_port):
        """Flood packet to all ports except input port"""
        actions = [datapath.ofproto_parser.OFPActionOutput(
            datapath.ofproto.OFPP_FLOOD)]
            
        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=msg.data
        )
        datapath.send_msg(out)

    def install_flow_rule(self, datapath, src_ip, dst_ip, dst_port, protocol, in_port):
        """Install flow rule for allowed connections"""
        parser = datapath.ofproto_parser
        
        # Match specific connection
        if protocol == 'tcp':
            match = parser.OFPMatch(
                eth_type=ether_types.ETH_TYPE_IP,
                ipv4_src=src_ip,
                ipv4_dst=dst_ip,
                ip_proto=6,  # TCP
                tcp_dst=dst_port
            )
        elif protocol == 'udp':
            match = parser.OFPMatch(
                eth_type=ether_types.ETH_TYPE_IP,
                ipv4_src=src_ip,
                ipv4_dst=dst_ip,
                ip_proto=17,  # UDP
                udp_dst=dst_port
            )
        elif protocol == 'icmp':
            match = parser.OFPMatch(
                eth_type=ether_types.ETH_TYPE_IP,
                ipv4_src=src_ip,
                ipv4_dst=dst_ip,
                ip_proto=1  # ICMP
            )
        else:
            return
            
        # Forward to destination
        dst_mac = self.ip_to_mac.get(dst_ip)
        if dst_mac and dst_mac in self.mac_to_port:
            out_port = self.mac_to_port[dst_mac]
            actions = [parser.OFPActionOutput(out_port)]
            
            # Install flow with timeout
            self.add_flow(datapath, 100, match, actions, idle_timeout=30)
            self.logger.debug(f"Installed flow rule: {src_ip} -> {dst_ip}:{dst_port} ({protocol})")
    
    def install_return_flow_rule(self, datapath, original_src, original_dst, original_port, protocol):
        """Install flow rule for return traffic (stateful connection)"""
        parser = datapath.ofproto_parser
        
        # Install a more permissive return rule (any port from server back to client)
        if protocol == 'tcp':
            match = parser.OFPMatch(
                eth_type=ether_types.ETH_TYPE_IP,
                ipv4_src=original_dst,  # Server responding back
                ipv4_dst=original_src,  # To original client
                ip_proto=6  # TCP (any port)
            )
        elif protocol == 'udp':
            match = parser.OFPMatch(
                eth_type=ether_types.ETH_TYPE_IP,
                ipv4_src=original_dst,  # Server responding back
                ipv4_dst=original_src,  # To original client
                ip_proto=17  # UDP (any port)
            )
        elif protocol == 'icmp':
            # For ICMP, install bidirectional rule
            match = parser.OFPMatch(
                eth_type=ether_types.ETH_TYPE_IP,
                ipv4_src=original_dst,  # Server responding back
                ipv4_dst=original_src,  # To original client
                ip_proto=1  # ICMP
            )
        else:
            return
        
        # Forward return traffic to original client
        src_mac = self.ip_to_mac.get(original_src)
        if src_mac and src_mac in self.mac_to_port:
            out_port = self.mac_to_port[src_mac]
            actions = [parser.OFPActionOutput(out_port)]
            
            # Install return flow with shorter timeout (stateful)
            self.add_flow(datapath, 90, match, actions, idle_timeout=60)
            self.logger.debug(f"Installed return flow rule: {original_dst} -> {original_src} ({protocol} return traffic)")

    def log_security_event(self, action, src_ip, dst_ip, dst_port, protocol):
        """Log security events to file for GUI consumption"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        src_role = self.ip_to_role.get(src_ip, 'UNKNOWN')
        
        # Create log entry
        log_entry = f"{timestamp} - {action}: {src_ip} ({src_role}) -> {dst_ip}:{dst_port} ({protocol})"
        
        # Write to security events log file
        try:
            with open(self.security_log_file, 'a') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write security log: {e}")
    
    def log_security_violation(self, src_ip, dst_ip, dst_port, protocol):
        """Log security policy violations"""
        violation = {
            'timestamp': datetime.now().isoformat(),
            'source_ip': src_ip,
            'destination_ip': dst_ip,
            'destination_port': dst_port,
            'protocol': protocol,
            'source_role': self.ip_to_role.get(src_ip, 'UNKNOWN'),
            'action': 'BLOCKED'
        }
        
        self.policy_violations.append(violation)
        
        # Log to file
        self.logger.error(f"SECURITY VIOLATION: {violation}")
        
        # Keep only last 1000 violations
        if len(self.policy_violations) > 1000:
            self.policy_violations = self.policy_violations[-1000:]

    def get_traffic_stats(self):
        """Return current traffic statistics"""
        return {
            'traffic_flows': dict(self.traffic_flows),
            'dependency_graph': {k: list(v) for k, v in self.dependency_graph.items()},
            'policy_violations': self.policy_violations[-10:],  # Last 10 violations
            'learned_hosts': dict(self.ip_to_mac)
        }