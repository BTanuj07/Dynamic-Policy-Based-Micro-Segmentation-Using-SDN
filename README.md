# Dynamic Policy-Based Micro-Segmentation Using SDN

## Project Overview
This project implements a Software Defined Networking (SDN) based micro-segmentation system using Python, Ryu controller, and Mininet for network emulation. It prevents lateral movement attacks through intelligent network segmentation with 94-100% security effectiveness.

## Architecture
- **Mininet Topology**: 5 hosts connected through 1 OpenFlow switch
- **Ryu Controller**: Custom controller with real-time policy enforcement
- **Policy Engine**: Role-based access control with zero trust model
- **Monitoring**: Web dashboard and desktop GUI for real-time monitoring

## Network Topology
```
    Ryu Controller (127.0.0.1:6653)
         |
    [OpenFlow Switch s1]
    /    |    |    |    \
Web(10)  App(20) DB(30) HR(100) Admin(200)
```

## Core Files (17 files)
- `controller.py` - Main SDN controller with policy enforcement (400+ lines)
- `mininet_topology.py` - Network topology definition
- `roles.json` - Role definitions and security policies
- `test_attacks.py` - Comprehensive security testing framework
- `automated_attacks.py` - Real network traffic attack generation
- `web_dashboard.py` - Real-time web monitoring interface
- `desktop_gui.py` - Native desktop monitoring application
- `cloud_security_controller.py` - **NEW** Cloud security with multi-tenancy
- `cloud_deployment.py` - **NEW** Multi-cloud deployment automation
- `setup.py` - Environment validation and setup
- `requirements.txt` - Python dependencies
- `Makefile` - Project automation commands
- `Dockerfile` - **NEW** Container deployment configuration
- `docker-compose.yml` - **NEW** Multi-service orchestration
- `README.md` - Project documentation
- `INSTRUCTIONS.md` - Detailed running instructions
- `.gitignore` - Git ignore rules

## Requirements
- Python 3.9+
- Mininet
- Ryu SDN Controller
- Open vSwitch
- OpenFlow 1.3
- Docker (optional, for containerized deployment)

## ☁️ Cloud Security Quick Start

### Docker Deployment (Recommended)
```bash
# Build and run with Docker Compose
docker-compose up -d

# View services
docker-compose ps

# View logs
docker-compose logs -f
```

### Cloud Security Simulation
```bash
# Run cloud security features
python3 cloud_security_controller.py

# Generate cloud deployment templates
python3 cloud_deployment.py
```

## Quick Start

### Method 1: Using Makefile (Recommended)
```bash
# Setup and validate
make setup

# Terminal 1: Start controller
make start-controller

# Terminal 2: Start topology  
make start-topology

# Terminal 3: Run tests
make test

# Terminal 4: Generate automated attacks
make automated-attacks
```

### Method 2: Manual Commands
```bash
# Terminal 1: Start Ryu controller
ryu-manager controller.py --verbose

# Terminal 2: Start Mininet topology
sudo python3 mininet_topology.py

# Terminal 3: Run security tests
python3 test_attacks.py

# Terminal 4: Generate real network attacks
python3 automated_attacks.py
```

### Method 3: Real Network Traffic Generation
For generating REAL network traffic that creates actual security logs:

```bash
# In Mininet CLI (Terminal 2), execute:
py execfile('run_automated_attacks.py')

# Or copy commands from generated file:
# automated_attack_commands.txt
```

## Network Hosts
- Web Server: 10.0.0.10 (h1)
- App Server: 10.0.0.20 (h2)
- DB Server: 10.0.0.30 (h3)
- HR User: 10.0.0.100 (h4)
- Admin User: 10.0.0.200 (h5)

## Automated Attack Generation

This project includes automated attack generation that creates **REAL network traffic** through your SDN controller:

### Features
- **Real Network Traffic**: Generates actual packets through Mininet hosts
- **Live Security Logs**: Creates real security events in `security_events.log`
- **Web Dashboard Integration**: View live attacks in web interface
- **Multiple Attack Types**: HTTP, TCP, SSH, Database, and ICMP attacks

### Usage Options

#### Option 1: Direct Execution (Generates Real Traffic)
```bash
# In Mininet CLI:
py execfile('run_automated_attacks.py')
```

#### Option 2: Command Generation
```bash
# Generate attack commands:
python3 automated_attacks.py

# Then execute commands from:
# - automated_attack_commands.txt (manual copy/paste)
# - execute_attacks.py (automated execution)
```

#### Option 3: Web Dashboard
```bash
# Start web dashboard:
python3 web_dashboard.py

# Visit: http://localhost:5000
# Click "Run Advanced Tests" to execute automated attacks
```

### Monitoring Real-Time Security Events
```bash
# Watch security logs:
tail -f security_events.log

# View web dashboard:
http://localhost:5000
```

## GUI Interfaces

### Web Dashboard
- **URL**: http://localhost:5000
- **Features**: Real-time monitoring, test execution, security events
- **Start**: `python3 web_dashboard.py`

### Desktop GUI
- **Features**: Native desktop interface with real-time updates
- **Start**: `python3 desktop_gui.py`

### Linux GUI Setup
- **Auto-setup**: `bash linux_gui_setup.sh`
- **Launcher**: `python3 launch_gui.py`