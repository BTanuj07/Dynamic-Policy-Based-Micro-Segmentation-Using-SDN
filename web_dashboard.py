#!/usr/bin/env python3
"""
Web-based GUI Dashboard for SDN Micro-Segmentation
Real-time monitoring with interactive web interface
"""

from flask import Flask, render_template, jsonify, request
import json
import os
import threading
import time
from datetime import datetime
import subprocess

app = Flask(__name__)

class SDNDashboard:
    def __init__(self):
        self.traffic_stats = {}
        self.security_events = []
        self.test_results = {}
        self.system_status = {
            'controller': 'Unknown',
            'topology': 'Unknown',
            'last_update': datetime.now().isoformat()
        }
    
    def load_test_results(self):
        """Load test results from JSON files"""
        try:
            if os.path.exists('security_test_report.json'):
                with open('security_test_report.json', 'r') as f:
                    self.test_results = json.load(f)
        except:
            pass
    
    def load_security_events(self):
        """Load recent security events"""
        try:
            if os.path.exists('security_events.log'):
                with open('security_events.log', 'r') as f:
                    lines = f.readlines()
                    # Filter and format security events
                    events = []
                    for line in lines:
                        line = line.strip()
                        if line and ('ALLOWED:' in line or 'BLOCKED:' in line):
                            events.append(line)
                    self.security_events = events[-50:]  # Last 50 events
            else:
                self.security_events = []
        except Exception as e:
            print(f"Error loading security events: {e}")
            self.security_events = []
    
    def check_system_status(self):
        """Check if controller and topology are running"""
        try:
            # Check for Ryu controller process
            result = subprocess.run(['pgrep', '-f', 'ryu-manager'], 
                                  capture_output=True, text=True)
            self.system_status['controller'] = 'Running' if result.returncode == 0 else 'Stopped'
            
            # Check for Mininet process
            result = subprocess.run(['pgrep', '-f', 'mininet'], 
                                  capture_output=True, text=True)
            self.system_status['topology'] = 'Running' if result.returncode == 0 else 'Stopped'
            
        except:
            pass
        
        self.system_status['last_update'] = datetime.now().isoformat()

# Global dashboard instance
dashboard = SDNDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """API endpoint for system status"""
    dashboard.check_system_status()
    return jsonify(dashboard.system_status)

@app.route('/api/test-results')
def get_test_results():
    """API endpoint for test results"""
    dashboard.load_test_results()
    return jsonify(dashboard.test_results)

@app.route('/api/security-events')
def get_security_events():
    """API endpoint for security events"""
    dashboard.load_security_events()
    return jsonify({
        'events': dashboard.security_events[-20:],  # Last 20 events
        'count': len(dashboard.security_events)
    })

@app.route('/api/run-test')
def run_test():
    """API endpoint to run security tests"""
    try:
        result = subprocess.run(['python3', 'test_attacks.py'], 
                              capture_output=True, text=True, timeout=30)
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/run-advanced-test')
def run_advanced_test():
    """API endpoint to run cloud security tests"""
    try:
        result = subprocess.run(['python3', 'cloud_security_controller.py'], 
                              capture_output=True, text=True, timeout=30)
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/run-cloud-security')
def run_cloud_security():
    """API endpoint to run cloud security simulation"""
    try:
        result = subprocess.run(['python3', 'cloud_security_controller.py'], 
                              capture_output=True, text=True, timeout=30)
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/cloud-events')
def get_cloud_events():
    """API endpoint for cloud security events"""
    try:
        cloud_events = []
        if os.path.exists('cloud_security_events.log'):
            with open('cloud_security_events.log', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line and ('BLOCKED' in line or 'ALLOWED' in line or 'VIOLATION' in line):
                        cloud_events.append(line)
        
        return jsonify({
            'events': cloud_events[-20:],  # Last 20 events
            'count': len(cloud_events)
        })
    except Exception as e:
        return jsonify({
            'events': [],
            'count': 0,
            'error': str(e)
        })

@app.route('/api/compliance-report')
def get_compliance_report():
    """API endpoint for compliance report"""
    try:
        if os.path.exists('cloud_compliance_report.json'):
            with open('cloud_compliance_report.json', 'r') as f:
                report = json.load(f)
            return jsonify(report)
        else:
            return jsonify({'error': 'No compliance report found'})
    except Exception as e:
        return jsonify({'error': str(e)})

def create_html_template():
    """Create HTML template for dashboard"""
    os.makedirs('templates', exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SDN Micro-Segmentation Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .card h3 { color: #333; margin-bottom: 15px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .status-running { color: #28a745; font-weight: bold; }
        .status-stopped { color: #dc3545; font-weight: bold; }
        .btn { background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #5a6fd8; }
        .btn-success { background: #28a745; }
        .btn-danger { background: #dc3545; }
        .event-log { max-height: 300px; overflow-y: auto; background: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px; }
        .metric { display: flex; justify-content: space-between; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }
        .metric-value { font-weight: bold; color: #667eea; }
        .progress-bar { width: 100%; height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #28a745, #20c997); transition: width 0.3s ease; }
        .loading { text-align: center; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ SDN Micro-Segmentation Dashboard</h1>
        <p>Real-time Network Security Monitoring</p>
    </div>
    
    <div class="container">
        <div class="grid">
            <!-- System Status Card -->
            <div class="card">
                <h3>🔧 System Status</h3>
                <div class="metric">
                    <span>Ryu Controller:</span>
                    <span id="controller-status" class="status-stopped">Checking...</span>
                </div>
                <div class="metric">
                    <span>Mininet Topology:</span>
                    <span id="topology-status" class="status-stopped">Checking...</span>
                </div>
                <div class="metric">
                    <span>Last Update:</span>
                    <span id="last-update">Never</span>
                </div>
                <button class="btn" onclick="refreshStatus()">🔄 Refresh Status</button>
            </div>
            
            <!-- Test Results Card -->
            <div class="card">
                <h3>📊 Security Test Results</h3>
                <div id="test-results">
                    <div class="loading">No test results available</div>
                </div>
                <div style="margin-top: 15px;">
                    <button class="btn" onclick="runBasicTest()">🧪 Run Basic Tests</button>
                    <button class="btn" onclick="runCloudSecurity()">☁️ Run Cloud Security</button>
                </div>
            </div>
            
            <!-- Cloud Security Events Card -->
            <div class="card">
                <h3>☁️ Cloud Security Events</h3>
                <div id="cloud-events" class="event-log">
                    <div class="loading">Loading cloud security events...</div>
                </div>
                <button class="btn" onclick="refreshCloudEvents()">🔄 Refresh Cloud Events</button>
            </div>
            
            <!-- Security Events Card -->
            <div class="card">
                <h3>🔒 Network Security Events</h3>
                <div id="security-events" class="event-log">
                    <div class="loading">Loading security events...</div>
                </div>
                <button class="btn" onclick="refreshEvents()">🔄 Refresh Events</button>
            </div>
            
            <!-- Compliance Status Card -->
            <div class="card">
                <h3>📋 Compliance Status</h3>
                <div id="compliance-status">
                    <div class="loading">Loading compliance status...</div>
                </div>
                <button class="btn" onclick="refreshCompliance()">🔄 Refresh Compliance</button>
            </div>
            
            <!-- Network Topology Card -->
            <div class="card">
                <h3>🌐 Network Topology</h3>
                <div style="text-align: center; padding: 20px;">
                    <div style="margin: 10px 0;">
                        <strong>Controller (Ryu)</strong><br>
                        <span style="font-size: 24px;">🎛️</span>
                    </div>
                    <div style="margin: 10px 0;">↕️</div>
                    <div style="margin: 10px 0;">
                        <strong>OpenFlow Switch (s1)</strong><br>
                        <span style="font-size: 24px;">🔀</span>
                    </div>
                    <div style="margin: 10px 0;">↕️</div>
                    <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
                        <div style="margin: 5px;">
                            <strong>Web</strong><br>
                            <span style="font-size: 20px;">🌐</span><br>
                            <small>10.0.0.10</small>
                        </div>
                        <div style="margin: 5px;">
                            <strong>App</strong><br>
                            <span style="font-size: 20px;">⚙️</span><br>
                            <small>10.0.0.20</small>
                        </div>
                        <div style="margin: 5px;">
                            <strong>DB</strong><br>
                            <span style="font-size: 20px;">🗄️</span><br>
                            <small>10.0.0.30</small>
                        </div>
                        <div style="margin: 5px;">
                            <strong>HR</strong><br>
                            <span style="font-size: 20px;">👤</span><br>
                            <small>10.0.0.100</small>
                        </div>
                        <div style="margin: 5px;">
                            <strong>Admin</strong><br>
                            <span style="font-size: 20px;">👨‍💼</span><br>
                            <small>10.0.0.200</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Auto-refresh data every 5 seconds
        setInterval(() => {
            refreshStatus();
            refreshEvents();
            refreshCloudEvents();
            loadTestResults();
            refreshCompliance();
        }, 5000);
        
        // Initial load
        window.onload = () => {
            refreshStatus();
            refreshEvents();
            refreshCloudEvents();
            loadTestResults();
            refreshCompliance();
        };
        
        function refreshStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('controller-status').textContent = data.controller;
                    document.getElementById('controller-status').className = 
                        data.controller === 'Running' ? 'status-running' : 'status-stopped';
                    
                    document.getElementById('topology-status').textContent = data.topology;
                    document.getElementById('topology-status').className = 
                        data.topology === 'Running' ? 'status-running' : 'status-stopped';
                    
                    document.getElementById('last-update').textContent = 
                        new Date(data.last_update).toLocaleString();
                })
                .catch(error => console.error('Error:', error));
        }
        
        function loadTestResults() {
            fetch('/api/test-results')
                .then(response => response.json())
                .then(data => {
                    if (data.summary) {
                        const summary = data.summary;
                        const successRate = summary.success_rate || 0;
                        
                        document.getElementById('test-results').innerHTML = `
                            <div class="metric">
                                <span>Total Tests:</span>
                                <span class="metric-value">${summary.total_tests || 0}</span>
                            </div>
                            <div class="metric">
                                <span>Passed Tests:</span>
                                <span class="metric-value">${summary.passed_tests || 0}</span>
                            </div>
                            <div class="metric">
                                <span>Success Rate:</span>
                                <span class="metric-value">${successRate.toFixed(1)}%</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${successRate}%"></div>
                            </div>
                        `;
                    }
                })
                .catch(error => console.error('Error:', error));
        }
        
        function refreshEvents() {
            fetch('/api/security-events')
                .then(response => response.json())
                .then(data => {
                    const eventsDiv = document.getElementById('security-events');
                    if (data.events && data.events.length > 0) {
                        eventsDiv.innerHTML = data.events.map(event => {
                            const color = event.includes('BLOCKED') ? '#dc3545' : 
                                         event.includes('ALLOWED') ? '#28a745' : '#333';
                            return `<div style="color: ${color}; margin: 2px 0;">${event.trim()}</div>`;
                        }).join('');
                    } else {
                        eventsDiv.innerHTML = '<div class="loading">No security events logged yet</div>';
                    }
                })
                .catch(error => console.error('Error:', error));
        }
        
        function runBasicTest() {
            document.getElementById('test-results').innerHTML = '<div class="loading">Running basic tests...</div>';
            fetch('/api/run-test')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        setTimeout(loadTestResults, 1000);
                    } else {
                        document.getElementById('test-results').innerHTML = 
                            `<div style="color: #dc3545;">Test failed: ${data.error}</div>`;
                    }
                })
                .catch(error => {
                    document.getElementById('test-results').innerHTML = 
                        `<div style="color: #dc3545;">Error: ${error}</div>`;
                });
        }
        
        function runAdvancedTest() {
            document.getElementById('test-results').innerHTML = '<div class="loading">Running advanced tests...</div>';
            fetch('/api/run-advanced-test')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        setTimeout(loadTestResults, 1000);
                    } else {
                        document.getElementById('test-results').innerHTML = 
                            `<div style="color: #dc3545;">Advanced test failed: ${data.error}</div>`;
                    }
                })
                .catch(error => {
                    document.getElementById('test-results').innerHTML = 
                        `<div style="color: #dc3545;">Error: ${error}</div>`;
                });
        }
        
        function runCloudSecurity() {
            document.getElementById('test-results').innerHTML = '<div class="loading">Running cloud security simulation...</div>';
            fetch('/api/run-cloud-security')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        setTimeout(() => {
                            loadTestResults();
                            refreshCloudEvents();
                            refreshCompliance();
                        }, 2000);
                        document.getElementById('test-results').innerHTML = 
                            '<div style="color: #28a745;">Cloud security simulation completed successfully!</div>';
                    } else {
                        document.getElementById('test-results').innerHTML = 
                            `<div style="color: #dc3545;">Cloud security test failed: ${data.error}</div>`;
                    }
                })
                .catch(error => {
                    document.getElementById('test-results').innerHTML = 
                        `<div style="color: #dc3545;">Error: ${error}</div>`;
                });
        }
        
        function refreshCloudEvents() {
            fetch('/api/cloud-events')
                .then(response => response.json())
                .then(data => {
                    const eventsDiv = document.getElementById('cloud-events');
                    if (data.events && data.events.length > 0) {
                        eventsDiv.innerHTML = data.events.map(event => {
                            let color = '#333';
                            if (event.includes('BLOCKED') || event.includes('VIOLATION')) {
                                color = '#dc3545';
                            } else if (event.includes('ALLOWED') || event.includes('COMPLIANT')) {
                                color = '#28a745';
                            } else if (event.includes('WARNING')) {
                                color = '#ffc107';
                            }
                            return `<div style="color: ${color}; margin: 2px 0;">${event.trim()}</div>`;
                        }).join('');
                    } else {
                        eventsDiv.innerHTML = '<div class="loading">No cloud security events logged yet</div>';
                    }
                })
                .catch(error => console.error('Error:', error));
        }
        
        function refreshCompliance() {
            fetch('/api/compliance-report')
                .then(response => response.json())
                .then(data => {
                    const complianceDiv = document.getElementById('compliance-status');
                    if (data.compliance_status) {
                        let html = '';
                        for (const [framework, status] of Object.entries(data.compliance_status)) {
                            const statusColor = status.status === 'COMPLIANT' ? '#28a745' : '#dc3545';
                            const statusIcon = status.status === 'COMPLIANT' ? '✅' : '❌';
                            html += `
                                <div class="metric">
                                    <span>${statusIcon} ${framework}:</span>
                                    <span style="color: ${statusColor}; font-weight: bold;">${status.status}</span>
                                </div>
                            `;
                        }
                        complianceDiv.innerHTML = html;
                    } else {
                        complianceDiv.innerHTML = '<div class="loading">No compliance data available</div>';
                    }
                })
                .catch(error => {
                    document.getElementById('compliance-status').innerHTML = 
                        '<div class="loading">Run cloud security simulation to generate compliance report</div>';
                });
        }
    </script>
</body>
</html>'''
    
    with open('templates/dashboard.html', 'w') as f:
        f.write(html_content)

def main():
    """Start the web dashboard"""
    print("Creating HTML template...")
    create_html_template()
    
    print("Starting SDN Web Dashboard...")
    print("Dashboard will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()