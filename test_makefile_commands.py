#!/usr/bin/env python3
"""
Test script to verify all Makefile commands work correctly
"""

import subprocess
import os
import time

def test_command(command, description, timeout=10):
    """Test a make command"""
    print(f"Testing: {description}")
    print(f"Command: make {command}")
    
    try:
        result = subprocess.run(['make', command], 
                              capture_output=True, text=True, timeout=timeout)
        
        if result.returncode == 0:
            print("✅ PASS")
            return True
        else:
            print(f"❌ FAIL - Return code: {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    finally:
        print("-" * 50)

def main():
    """Test all Makefile commands"""
    print("🧪 TESTING MAKEFILE COMMANDS")
    print("=" * 60)
    
    # Test commands that should work without dependencies
    commands_to_test = [
        ("help", "Display help information"),
        ("validate", "Validate project files"),
        ("cloud-deploy", "Generate cloud deployment templates"),
        ("test-commands", "Generate test commands"),
        ("sample-logs", "Create sample logs message"),
    ]
    
    passed = 0
    total = len(commands_to_test)
    
    for command, description in commands_to_test:
        if test_command(command, description):
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    print(f"📊 TEST RESULTS:")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🟢 ALL TESTS PASSED!")
    elif passed >= total * 0.8:
        print("🟡 MOST TESTS PASSED")
    else:
        print("🔴 MULTIPLE FAILURES")
    
    print(f"\n📋 COMMANDS REQUIRING RUNNING SERVICES:")
    print("- make start-controller (requires Ryu)")
    print("- make start-topology (requires sudo + Mininet)")
    print("- make test (requires controller + topology)")
    print("- make cloud-security (requires Python dependencies)")
    print("- make docker-up (requires Docker)")
    
    print(f"\n🎯 TO TEST FULL SYSTEM:")
    print("1. make setup")
    print("2. make start-controller (Terminal 1)")
    print("3. make start-topology (Terminal 2)")
    print("4. make test (Terminal 3)")
    print("5. make cloud-security (Terminal 4)")

if __name__ == "__main__":
    main()