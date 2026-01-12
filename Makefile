# Makefile for SDN Micro-Segmentation Project
# Provides convenient commands for project management

.PHONY: help setup clean start-controller start-topology test logs stop monitor web-gui desktop-gui cloud-security cloud-deploy docker-build docker-up docker-down docker-logs automated-attacks test-commands sample-logs security-assessment archive install validate

# Default target
help:
	@echo "SDN Micro-Segmentation Project Commands:"
	@echo ""
	@echo "  make setup          - Check prerequisites and setup environment"
	@echo "  make start-controller - Start Ryu SDN controller"
	@echo "  make start-topology - Start Mininet topology (requires sudo)"
	@echo "  make test           - Run security tests"
	@echo "  make automated-attacks - Generate real network attacks"
	@echo "  make cloud-security - Run cloud security simulation"
	@echo "  make cloud-deploy   - Generate cloud deployment templates"
	@echo "  make docker-up      - Start with Docker Compose"
	@echo "  make logs           - View security logs"
	@echo "  make clean          - Clean up processes and temporary files"
	@echo "  make stop           - Stop all running processes"
	@echo ""
	@echo "Quick Start:"
	@echo "  1. make setup"
	@echo "  2. make start-controller (in terminal 1)"
	@echo "  3. make start-topology (in terminal 2)"
	@echo "  4. make test (in terminal 3)"
	@echo "  5. make automated-attacks (generate real network attacks)"
	@echo ""
	@echo "Real Network Traffic Generation:"
	@echo "  In Mininet CLI: py execfile('automated_attacks.py')"
	@echo "  Monitor logs: tail -f security_events.log"
	@echo "  Web dashboard: http://localhost:5000"

# Setup environment
setup:
	@echo "Setting up SDN Micro-Segmentation project..."
	python3 setup.py

# Start Ryu controller
start-controller:
	@echo "Starting Ryu SDN Controller..."
	@echo "Press Ctrl+C to stop"
	ryu-manager controller.py --verbose

# Start Mininet topology
start-topology:
	@echo "Starting Mininet topology..."
	@echo "This requires sudo privileges"
	sudo python3 mininet_topology.py

# Run security tests
test:
	@echo "Running security tests..."
	python3 test_attacks.py

# View logs
logs:
	@echo "Viewing security logs (Press Ctrl+C to exit)..."
	@if [ -f security_events.log ]; then \
		tail -f security_events.log; \
	else \
		echo "No security_events.log found. Start the controller first."; \
	fi

# Monitor real-time attacks
monitor:
	@echo "Monitoring real-time security events..."
	@echo "Execute attacks in Mininet CLI to see live events!"
	@echo "Commands: py execfile('automated_attacks.py')"
	@echo "Press Ctrl+C to stop monitoring..."
	@tail -f security_events.log 2>/dev/null || echo "Waiting for security_events.log..."

# GUI interfaces
web-gui:
	@echo "Starting Web Dashboard at http://localhost:5000"
	python3 web_dashboard.py

desktop-gui:
	@echo "Starting Desktop GUI..."
	python3 desktop_gui.py

# Cloud security features
cloud-security:
	@echo "Running cloud security simulation..."
	python3 cloud_security_controller.py

# Generate cloud deployment templates
cloud-deploy:
	@echo "Generating cloud deployment configurations..."
	python3 cloud_deployment.py

# Docker deployment
docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting services with Docker Compose..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

docker-logs:
	@echo "Viewing Docker logs..."
	docker-compose logs -f

# Clean up
clean:
	@echo "Cleaning up..."
	@sudo mn -c 2>/dev/null || true
	@pkill -f "ryu-manager" 2>/dev/null || true
	@rm -f *.log
	@rm -f *.json.bak
	@rm -f security_test_report.json
	@echo "Cleanup completed"

# Stop all processes
stop:
	@echo "Stopping all processes..."
	@sudo mn -c 2>/dev/null || true
	@pkill -f "ryu-manager" 2>/dev/null || true
	@echo "All processes stopped"

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip3 install -r requirements.txt

# Validate project files
validate:
	@echo "Validating project files..."
	@python3 -c "import json; json.load(open('roles.json'))" && echo "✅ roles.json valid"
	@python3 -m py_compile controller.py && echo "✅ controller.py valid"
	@python3 -m py_compile mininet_topology.py && echo "✅ mininet_topology.py valid"
	@python3 -m py_compile test_attacks.py && echo "✅ test_attacks.py valid"

# Advanced testing
automated-attacks:
	@echo "Generating automated attack commands..."
	python3 automated_attacks.py

# Safe CLI testing (no conflicts)
test-commands:
	@echo "Generating test commands for manual execution..."
	@echo "Check test_attacks.py for available test scenarios"

# Create sample logs for GUI testing
sample-logs:
	@echo "Creating sample security logs for GUI testing..."
	@echo "Run controller and generate traffic to create real logs"

# Full security assessment
security-assessment: test automated-attacks test-commands
	@echo "Complete security assessment completed"
	@echo "Check security_test_report.json for results"

# Create project archive
archive:
	@echo "Creating project archive..."
	@tar -czf sdn_microsegmentation_project.tar.gz \
		*.py *.json *.md *.txt *.sh Makefile \
		--exclude="*.log" --exclude="*.pyc" --exclude="__pycache__"
	@echo "Archive created: sdn_microsegmentation_project.tar.gz"