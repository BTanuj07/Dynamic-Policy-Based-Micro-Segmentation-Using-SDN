#!/usr/bin/env python3
"""
Setup script for SDN Micro-Segmentation Project
Checks system prerequisites and prepares the environment
"""

import os
import sys
import subprocess
import json

def check_python_version():
    """Check if Python version is 3.9+"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required. Current version:", sys.version)
        return False
    print("✅ Python version:", sys.version.split()[0])
    return True

def check_command(command):
    """Check if a command exists in PATH"""
    try:
        subprocess.run([command, '--version'], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_prerequisites():
    """Check all system prerequisites"""
    print("Checking system prerequisites...")
    
    checks = {
        'Python 3.9+': check_python_version(),
        'Mininet': check_command('mn'),
        'Open vSwitch': check_command('ovs-vsctl'),
        'Ryu Controller': check_command('ryu-manager')
    }
    
    all_good = True
    for name, status in checks.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {name}")
        if not status:
            all_good = False
    
    return all_good

def install_python_deps():
    """Install Python dependencies"""
    print("\nInstalling Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Python dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        return False

def validate_config_files():
    """Validate configuration files"""
    print("\nValidating configuration files...")
    
    # Check roles.json
    try:
        with open('roles.json', 'r') as f:
            roles_data = json.load(f)
        
        required_keys = ['roles', 'server_dependencies']
        for key in required_keys:
            if key not in roles_data:
                print(f"❌ Missing '{key}' in roles.json")
                return False
        
        print("✅ roles.json is valid")
    except Exception as e:
        print(f"❌ Invalid roles.json: {e}")
        return False
    
    # Check other required files
    required_files = [
        'controller.py',
        'mininet_topology.py', 
        'test_attacks.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} found")
        else:
            print(f"❌ {file} missing")
            return False
    
    return True

def create_log_directory():
    """Create directory for log files"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"✅ Created {log_dir} directory")
    else:
        print(f"✅ {log_dir} directory exists")

def print_next_steps():
    """Print instructions for running the project"""
    print("\n" + "="*50)
    print("SETUP COMPLETED SUCCESSFULLY!")
    print("="*50)
    print("\nNext steps to run the project:")
    print("\n1. Start the SDN Controller:")
    print("   ryu-manager controller.py --verbose")
    print("\n2. In another terminal, start Mininet:")
    print("   sudo python3 mininet_topology.py")
    print("\n3. Test the system:")
    print("   python3 test_attacks.py")
    print("\n4. View logs:")
    print("   tail -f security_events.log")
    print("\nFor detailed instructions, see INSTRUCTIONS.md")

def main():
    """Main setup function"""
    print("SDN Micro-Segmentation Project Setup")
    print("="*40)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please install missing components:")
        print("\nUbuntu/Debian:")
        print("  sudo apt update")
        print("  sudo apt install python3 python3-pip mininet openvswitch-switch")
        print("  pip3 install ryu")
        return False
    
    # Install Python dependencies
    if os.path.exists('requirements.txt'):
        if not install_python_deps():
            return False
    
    # Validate configuration
    if not validate_config_files():
        return False
    
    # Create log directory
    create_log_directory()
    
    # Success
    print_next_steps()
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)