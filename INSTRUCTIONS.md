# How to Run the SDN Micro-Segmentation Project

## Prerequisites
Make sure you have installed on your Linux system:
- Python 3.9+
- Ryu SDN Controller: `pip3 install ryu`
- Mininet: `sudo apt install mininet`
- Open vSwitch: `sudo apt install openvswitch-switch`

## Step-by-Step Instructions

### 1. Start the Ryu Controller
Open a terminal and run:
```bash
ryu-manager controller.py --verbose
```
Keep this terminal open. You should see:
```
loading app controller.py
instantiating app controller.py of MicroSegmentationController
Micro-Segmentation Controller Started
```

### 2. Start the Mininet Topology
Open a **new terminal** and run:
```bash
sudo python3 mininet_topology.py
```

You should see the network being created and then enter the Mininet CLI:
```
mininet> 
```

### 3. Test Basic Connectivity
In the Mininet CLI, test the policies:

**Test legitimate access (should work):**
```bash
mininet> h4 ping -c 1 h1    # HR user to Web server (ALLOWED)
mininet> h5 ping -c 1 h1    # Admin to Web server (ALLOWED)
```

**Test blocked access (should fail):**
```bash
mininet> h4 ping -c 1 h3    # HR user to DB server (BLOCKED)
mininet> h4 ping -c 1 h2    # HR user to App server (BLOCKED)
```

**Test all connections:**
```bash
mininet> pingall
```

### 4. Run Security Tests (Optional)
Exit Mininet first:
```bash
mininet> exit
```

Then run the automated security tests:
```bash
python3 test_attacks.py
```

### 5. View Logs
Check the controller logs:
```bash
tail -f security_events.log
```

## Expected Results

### Allowed Connections:
- HR (h4) → Web Server (h1): ports 80, 443
- Admin (h5) → Web Server (h1): ports 80, 443, 22
- Admin (h5) → App Server (h2): port 8080  
- Admin (h5) → DB Server (h3): port 3306
- Web Server (h1) → App Server (h2): port 8080
- App Server (h2) → DB Server (h3): port 3306

### Blocked Connections:
- HR (h4) → App Server (h2): any port
- HR (h4) → DB Server (h3): any port
- Any direct DB access from users
- Cross-user communication

## Troubleshooting

### Controller won't start:
```bash
# Kill any existing ryu processes
sudo pkill -f ryu-manager
# Try again
ryu-manager controller.py --verbose
```

### Mininet issues:
```bash
# Clean mininet
sudo mn -c
# Try again
sudo python3 mininet_topology.py
```

### Permission errors:
```bash
# Make sure you're using sudo for mininet
sudo python3 mininet_topology.py
```

## Project Files Explanation

- **controller.py**: Main SDN controller with policy enforcement
- **mininet_topology.py**: Network topology with 5 hosts and 1 switch
- **roles.json**: Role definitions and access policies
- **test_attacks.py**: Automated security testing script
- **README.md**: Project overview and documentation

## Success Indicators

1. **Controller starts** without errors
2. **Mininet topology** creates successfully  
3. **Legitimate traffic** is allowed (HR → Web, Admin → All)
4. **Attack traffic** is blocked (HR → DB, lateral movement)
5. **Security logs** show policy violations
6. **Flow rules** are installed dynamically

The system demonstrates micro-segmentation by allowing only authorized communication while blocking lateral movement attacks.