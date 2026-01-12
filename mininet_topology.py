#!/usr/bin/env python3
"""
Mininet Topology for SDN Micro-Segmentation Project

This script creates a simple network topology with:
- 1 OpenFlow switch (s1)
- 5 hosts representing different roles and services
- Connection to remote Ryu controller

Network Layout:
    Controller (Remote Ryu)
         |
    [Switch s1]
    /    |    |    |    \
  h1    h2    h3    h4    h5
 Web   App    DB    HR   Admin
(.10) (.20)  (.30) (.100)(.200)
"""

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time

def create_topology():
    """
    Create and configure the network topology
    """
    info('*** Creating network topology\n')
    
    # Create Mininet instance with remote controller
    net = Mininet(
        controller=RemoteController,
        switch=OVSKernelSwitch,
        link=TCLink,
        autoSetMacs=True,
        autoStaticArp=True
    )
    
    info('*** Adding controller\n')
    # Connect to Ryu controller (default: localhost:6653)
    c0 = net.addController(
        'c0',
        controller=RemoteController,
        ip='127.0.0.1',
        port=6653
    )
    
    info('*** Adding switch\n')
    # Add OpenFlow switch
    s1 = net.addSwitch('s1', protocols='OpenFlow13')
    
    info('*** Adding hosts\n')
    # Add server hosts
    h1 = net.addHost('h1', ip='10.0.0.10/24', mac='00:00:00:00:00:01')  # Web Server
    h2 = net.addHost('h2', ip='10.0.0.20/24', mac='00:00:00:00:00:02')  # App Server  
    h3 = net.addHost('h3', ip='10.0.0.30/24', mac='00:00:00:00:00:03')  # DB Server
    
    # Add user hosts
    h4 = net.addHost('h4', ip='10.0.0.100/24', mac='00:00:00:00:00:04') # HR User
    h5 = net.addHost('h5', ip='10.0.0.200/24', mac='00:00:00:00:00:05') # Admin User
    
    info('*** Creating links\n')
    # Connect all hosts to the switch
    net.addLink(h1, s1)
    net.addLink(h2, s1) 
    net.addLink(h3, s1)
    net.addLink(h4, s1)
    net.addLink(h5, s1)
    
    return net

def setup_services(net):
    """
    Setup basic services on hosts to simulate real applications
    """
    info('*** Setting up services\n')
    
    # Get hosts
    web = net.get('h1')
    app = net.get('h2') 
    db = net.get('h3')
    
    # Start simple HTTP server on web server (port 80)
    info('*** Starting web server on h1:80\n')
    web.cmd('python3 -m http.server 80 &')
    
    # Start app server simulation (port 8080)
    info('*** Starting app server on h2:8080\n') 
    app.cmd('python3 -m http.server 8080 &')
    
    # Start database simulation (netcat listener on port 3306)
    info('*** Starting database listener on h3:3306\n')
    db.cmd('nc -l -p 3306 &')
    
    # Give services time to start
    time.sleep(2)

def main():
    """
    Main function to create topology and start network
    """
    setLogLevel('info')
    
    # Create topology
    net = create_topology()
    
    info('*** Starting network\n')
    net.start()
    
    # Wait for controller connection
    info('*** Waiting for controller connection...\n')
    time.sleep(3)
    
    # Setup services
    setup_services(net)
    
    info('*** Network topology created successfully!\n')
    info('*** Hosts and their IPs:\n')
    info('    h1 (Web Server): 10.0.0.10\n')
    info('    h2 (App Server): 10.0.0.20\n') 
    info('    h3 (DB Server): 10.0.0.30\n')
    info('    h4 (HR User): 10.0.0.100\n')
    info('    h5 (Admin User): 10.0.0.200\n')
    info('*** \n')
    info('*** You can now test connectivity:\n')
    info('    mininet> h4 ping h1  # HR to Web (should work)\n')
    info('    mininet> h4 ping h3  # HR to DB (should be blocked)\n')
    info('    mininet> pingall     # Test all connections\n')
    info('*** \n')
    
    # Start CLI for interactive testing
    CLI(net)
    
    # Cleanup
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    main()