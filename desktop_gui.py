#!/usr/bin/env python3
"""
Desktop GUI for SDN Micro-Segmentation System
Cross-platform desktop interface using Tkinter
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
import subprocess
import threading
import time
from datetime import datetime

class SDNDesktopGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SDN Micro-Segmentation Control Panel")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.controller_status = tk.StringVar(value="Unknown")
        self.topology_status = tk.StringVar(value="Unknown")
        self.test_results = {}
        
        self.create_widgets()
        self.start_auto_refresh()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x', padx=5, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🛡️ SDN Micro-Segmentation Dashboard", 
                              font=('Arial', 18, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left panel
        left_frame = tk.Frame(main_frame, bg='#f0f0f0')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Right panel
        right_frame = tk.Frame(main_frame, bg='#f0f0f0')
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # System Status Section
        self.create_status_section(left_frame)
        
        # Test Results Section
        self.create_test_section(left_frame)
        
        # Security Events Section
        self.create_events_section(right_frame)
        
        # Network Topology Section
        self.create_topology_section(right_frame)
    
    def create_status_section(self, parent):
        """Create system status section"""
        status_frame = tk.LabelFrame(parent, text="🔧 System Status", 
                                   font=('Arial', 12, 'bold'), bg='white', padx=10, pady=10)
        status_frame.pack(fill='x', pady=(0, 10))
        
        # Controller status
        tk.Label(status_frame, text="Ryu Controller:", font=('Arial', 10), bg='white').grid(row=0, column=0, sticky='w', pady=2)
        controller_label = tk.Label(status_frame, textvariable=self.controller_status, 
                                  font=('Arial', 10, 'bold'), bg='white', fg='red')
        controller_label.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Topology status
        tk.Label(status_frame, text="Mininet Topology:", font=('Arial', 10), bg='white').grid(row=1, column=0, sticky='w', pady=2)
        topology_label = tk.Label(status_frame, textvariable=self.topology_status, 
                                font=('Arial', 10, 'bold'), bg='white', fg='red')
        topology_label.grid(row=1, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Refresh button
        refresh_btn = tk.Button(status_frame, text="🔄 Refresh Status", 
                              command=self.refresh_status, bg='#3498db', fg='white', 
                              font=('Arial', 9, 'bold'))
        refresh_btn.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky='ew')
    
    def create_test_section(self, parent):
        """Create test results section"""
        test_frame = tk.LabelFrame(parent, text="📊 Security Tests", 
                                 font=('Arial', 12, 'bold'), bg='white', padx=10, pady=10)
        test_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Test results display
        self.test_text = scrolledtext.ScrolledText(test_frame, height=8, width=50, 
                                                 font=('Courier', 9), bg='#f8f9fa')
        self.test_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Test buttons
        button_frame = tk.Frame(test_frame, bg='white')
        button_frame.pack(fill='x')
        
        basic_test_btn = tk.Button(button_frame, text="🧪 Run Basic Tests", 
                                 command=self.run_basic_test, bg='#28a745', fg='white', 
                                 font=('Arial', 9, 'bold'))
        basic_test_btn.pack(side='left', padx=(0, 5))
        
        advanced_test_btn = tk.Button(button_frame, text="🔥 Run Advanced Tests", 
                                    command=self.run_advanced_test, bg='#dc3545', fg='white', 
                                    font=('Arial', 9, 'bold'))
        advanced_test_btn.pack(side='left')
    
    def create_events_section(self, parent):
        """Create security events section"""
        events_frame = tk.LabelFrame(parent, text="🔒 Security Events", 
                                   font=('Arial', 12, 'bold'), bg='white', padx=10, pady=10)
        events_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Events display
        self.events_text = scrolledtext.ScrolledText(events_frame, height=15, width=50, 
                                                   font=('Courier', 8), bg='#f8f9fa')
        self.events_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Refresh events button
        refresh_events_btn = tk.Button(events_frame, text="🔄 Refresh Events", 
                                     command=self.refresh_events, bg='#17a2b8', fg='white', 
                                     font=('Arial', 9, 'bold'))
        refresh_events_btn.pack()
    
    def create_topology_section(self, parent):
        """Create network topology section"""
        topology_frame = tk.LabelFrame(parent, text="🌐 Network Topology", 
                                     font=('Arial', 12, 'bold'), bg='white', padx=10, pady=10)
        topology_frame.pack(fill='x')
        
        # Topology diagram (text-based)
        topology_text = """
        Controller (Ryu)
             🎛️
             ↕️
        OpenFlow Switch
             🔀
             ↕️
    🌐      ⚙️      🗄️      👤      👨‍💼
   Web     App      DB      HR     Admin
  (.10)   (.20)   (.30)   (.100)  (.200)
        """
        
        tk.Label(topology_frame, text=topology_text, font=('Courier', 10), 
               bg='white', justify='center').pack()
    
    def refresh_status(self):
        """Refresh system status"""
        def check_status():
            try:
                # Check Ryu controller
                result = subprocess.run(['pgrep', '-f', 'ryu-manager'], 
                                      capture_output=True, text=True)
                controller_running = result.returncode == 0
                
                # Check Mininet
                result = subprocess.run(['pgrep', '-f', 'mininet'], 
                                      capture_output=True, text=True)
                topology_running = result.returncode == 0
                
                # Update GUI in main thread
                self.root.after(0, lambda: self.update_status(controller_running, topology_running))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Status check failed: {e}"))
        
        threading.Thread(target=check_status, daemon=True).start()
    
    def update_status(self, controller_running, topology_running):
        """Update status display"""
        self.controller_status.set("Running" if controller_running else "Stopped")
        self.topology_status.set("Running" if topology_running else "Stopped")
        
        # Update colors
        for widget in self.root.winfo_children():
            self.update_status_colors(widget, controller_running, topology_running)
    
    def update_status_colors(self, widget, controller_running, topology_running):
        """Recursively update status label colors"""
        if isinstance(widget, tk.Label):
            if widget['textvariable'] == str(self.controller_status):
                widget.config(fg='green' if controller_running else 'red')
            elif widget['textvariable'] == str(self.topology_status):
                widget.config(fg='green' if topology_running else 'red')
        
        for child in widget.winfo_children():
            self.update_status_colors(child, controller_running, topology_running)
    
    def run_basic_test(self):
        """Run basic security tests"""
        def run_test():
            try:
                self.root.after(0, lambda: self.test_text.insert(tk.END, "Running basic tests...\n"))
                result = subprocess.run(['python3', 'test_attacks.py'], 
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    self.root.after(0, lambda: self.test_text.insert(tk.END, "✅ Basic tests completed!\n"))
                    self.root.after(0, self.load_test_results)
                else:
                    self.root.after(0, lambda: self.test_text.insert(tk.END, f"❌ Test failed: {result.stderr}\n"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.test_text.insert(tk.END, f"❌ Error: {e}\n"))
        
        threading.Thread(target=run_test, daemon=True).start()
    
    def run_advanced_test(self):
        """Run advanced security tests"""
        def run_test():
            try:
                self.root.after(0, lambda: self.test_text.insert(tk.END, "Running advanced tests...\n"))
                result = subprocess.run(['python3', 'advanced_attacks.py'], 
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    self.root.after(0, lambda: self.test_text.insert(tk.END, "✅ Advanced tests completed!\n"))
                    self.root.after(0, self.load_test_results)
                else:
                    self.root.after(0, lambda: self.test_text.insert(tk.END, f"❌ Test failed: {result.stderr}\n"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.test_text.insert(tk.END, f"❌ Error: {e}\n"))
        
        threading.Thread(target=run_test, daemon=True).start()
    
    def load_test_results(self):
        """Load and display test results"""
        try:
            if os.path.exists('security_test_report.json'):
                with open('security_test_report.json', 'r') as f:
                    data = json.load(f)
                    
                if 'summary' in data:
                    summary = data['summary']
                    result_text = f"""
📊 Test Results Summary:
Total Tests: {summary.get('total_tests', 0)}
Passed Tests: {summary.get('passed_tests', 0)}
Success Rate: {summary.get('success_rate', 0):.1f}%
Duration: {summary.get('duration', 0):.2f}s

"""
                    self.test_text.insert(tk.END, result_text)
                    self.test_text.see(tk.END)
        except Exception as e:
            self.test_text.insert(tk.END, f"Error loading results: {e}\n")
    
    def refresh_events(self):
        """Refresh security events"""
        try:
            self.events_text.delete(1.0, tk.END)
            
            if os.path.exists('security_events.log'):
                with open('security_events.log', 'r') as f:
                    lines = f.readlines()
                    recent_events = lines[-30:]  # Last 30 events
                    
                for event in recent_events:
                    self.events_text.insert(tk.END, event)
            else:
                self.events_text.insert(tk.END, "No security events logged yet.\n")
                self.events_text.insert(tk.END, "Start the controller and run tests to generate events.\n")
                
            self.events_text.see(tk.END)
            
        except Exception as e:
            self.events_text.insert(tk.END, f"Error loading events: {e}\n")
    
    def start_auto_refresh(self):
        """Start automatic refresh of data"""
        def auto_refresh():
            self.refresh_status()
            self.refresh_events()
            # Schedule next refresh
            self.root.after(5000, auto_refresh)  # Every 5 seconds
        
        # Start first refresh after 1 second
        self.root.after(1000, auto_refresh)

def main():
    """Start the desktop GUI"""
    root = tk.Tk()
    app = SDNDesktopGUI(root)
    
    print("Starting SDN Desktop GUI...")
    print("Close the window to exit")
    
    root.mainloop()

if __name__ == "__main__":
    main()