#!/usr/bin/env python3

import sys
import time
import psutil
import socket
import requests
import subprocess
import threading
import scapy.all as scapy
from datetime import datetime
from collections import defaultdict
import netifaces
import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import dns.resolver
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np
import re
import os
from scapy.layers import http
from scapy.layers.tls.record import TLS
import hashlib
from io import BytesIO
import magic  # for file type detection

class NetworkMonitor(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Network Activity Monitor")
        self.geometry("1400x900")
        self.configure(bg='#2b2b2b')
        
        # Create cache directory
        self.cache_dir = os.path.join(os.path.expanduser("~"), ".network_monitor_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Store device information
        self.devices = {}
        self.mac_vendors = {}
        self.device_traffic = defaultdict(int)
        self.url_cache = {}
        self.image_cache = {}
        self.known_services = {
            80: "HTTP",
            443: "HTTPS",
            53: "DNS",
            22: "SSH",
            21: "FTP",
            3306: "MySQL",
            5432: "PostgreSQL",
            27017: "MongoDB",
            6379: "Redis",
            1433: "MSSQL",
            3389: "RDP",
            5900: "VNC"
        }
        
        # Initialize MAC vendor database
        self.load_mac_vendors()
        
        # Create main container with dark theme
        self.style = ttk.Style()
        self.style.configure("Dark.TFrame", background='#2b2b2b')
        self.style.configure("Dark.TNotebook", background='#2b2b2b', foreground='white')
        self.style.configure("Dark.TNotebook.Tab", background='#3c3f41', foreground='white', padding=[10, 2])
        self.style.map("Dark.TNotebook.Tab",
                      background=[("selected", "#4b6eaf")],
                      foreground=[("selected", "white")])
        
        self.main_container = ttk.Frame(self, style="Dark.TFrame")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.tab_control = ttk.Notebook(self.main_container, style="Dark.TNotebook")
        
        # Dashboard Tab
        self.dashboard_tab = ttk.Frame(self.tab_control, style="Dark.TFrame")
        self.tab_control.add(self.dashboard_tab, text='Dashboard')
        
        # Live Devices Tab
        self.devices_tab = ttk.Frame(self.tab_control, style="Dark.TFrame")
        self.tab_control.add(self.devices_tab, text='Live Devices')
        
        # Connections Tab
        self.connections_tab = ttk.Frame(self.tab_control, style="Dark.TFrame")
        self.tab_control.add(self.connections_tab, text='Active Connections')
        
        # Traffic Analysis Tab
        self.traffic_tab = ttk.Frame(self.tab_control, style="Dark.TFrame")
        self.tab_control.add(self.traffic_tab, text='Traffic Analysis')
        
        # Content Analysis Tab
        self.content_tab = ttk.Frame(self.tab_control, style="Dark.TFrame")
        self.tab_control.add(self.content_tab, text='Content Analysis')
        
        self.tab_control.pack(expand=True, fill=tk.BOTH)
        
        # Setup each tab
        self.setup_dashboard_tab()
        self.setup_devices_tab()
        self.setup_connections_tab()
        self.setup_traffic_tab()
        self.setup_content_tab()
        
        # Initialize data structures for tracking
        self.connection_history = defaultdict(list)
        self.device_categories = defaultdict(str)
        self.device_activity = defaultdict(list)
        self.alerts = []
        
        # Start monitoring threads
        self.running = True
        threading.Thread(target=self.scan_network, daemon=True).start()
        threading.Thread(target=self.monitor_connections, daemon=True).start()
        threading.Thread(target=self.capture_traffic, daemon=True).start()
        threading.Thread(target=self.update_dashboard, daemon=True).start()

    def setup_dashboard_tab(self):
        # Create frames for different sections
        top_frame = ttk.Frame(self.dashboard_tab, style="Dark.TFrame")
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Network Overview Section
        self.network_stats = tk.Label(top_frame, text="Network Overview", 
                                    bg='#2b2b2b', fg='white', font=('Arial', 12, 'bold'))
        self.network_stats.pack(pady=5)
        
        # Create a frame for device summary
        self.device_summary = scrolledtext.ScrolledText(top_frame, height=4, 
                                                      bg='#3c3f41', fg='white', font=('Courier', 10))
        self.device_summary.pack(fill=tk.X, padx=5, pady=5)
        
        # Create bottom frame for graphs
        bottom_frame = ttk.Frame(self.dashboard_tab, style="Dark.TFrame")
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Traffic Graph
        self.fig_traffic = plt.Figure(figsize=(6, 4), facecolor='#2b2b2b')
        self.ax_traffic = self.fig_traffic.add_subplot(111)
        self.ax_traffic.set_facecolor('#3c3f41')
        self.canvas_traffic = FigureCanvasTkAgg(self.fig_traffic, bottom_frame)
        self.canvas_traffic.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Alert Section
        alert_frame = ttk.Frame(bottom_frame, style="Dark.TFrame")
        alert_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(alert_frame, text="Recent Activity & Alerts", 
                bg='#2b2b2b', fg='white', font=('Arial', 12, 'bold')).pack(pady=5)
        
        self.alert_text = scrolledtext.ScrolledText(alert_frame, height=10, 
                                                  bg='#3c3f41', fg='white', font=('Courier', 10))
        self.alert_text.pack(fill=tk.BOTH, expand=True)

    def setup_devices_tab(self):
        # Devices list with categories
        columns = ('Category', 'IP', 'MAC', 'Vendor', 'Hostname', 'Status', 'Activity', 'Last Seen')
        self.devices_tree = ttk.Treeview(self.devices_tab, columns=columns, show='headings')
        
        for col in columns:
            self.devices_tree.heading(col, text=col)
            self.devices_tree.column(col, width=100)
        
        self.devices_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add right-click menu for device categorization
        self.device_menu = tk.Menu(self, tearoff=0)
        categories = ['Computer', 'Phone', 'IoT Device', 'Network Equipment', 'Smart TV', 'Game Console', 'Unknown']
        for category in categories:
            self.device_menu.add_command(label=category, 
                                       command=lambda c=category: self.set_device_category(c))
        
        self.devices_tree.bind("<Button-3>", self.show_device_menu)

    def setup_connections_tab(self):
        # Top frame for connection summary
        top_frame = ttk.Frame(self.connections_tab, style="Dark.TFrame")
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.conn_summary = scrolledtext.ScrolledText(top_frame, height=3, 
                                                    bg='#3c3f41', fg='white', font=('Courier', 10))
        self.conn_summary.pack(fill=tk.X)
        
        # Connections list with enhanced information
        columns = ('Local Device', 'Local IP', 'Local Port', 'Remote Host', 'Service', 'Status', 'Process', 'Duration')
        self.conn_tree = ttk.Treeview(self.connections_tab, columns=columns, show='headings')
        
        for col in columns:
            self.conn_tree.heading(col, text=col)
            self.conn_tree.column(col, width=100)
        
        self.conn_tree.pack(fill=tk.BOTH, expand=True)

    def setup_traffic_tab(self):
        # Create frames for different sections
        top_frame = ttk.Frame(self.traffic_tab, style="Dark.TFrame")
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Traffic summary
        self.traffic_summary = scrolledtext.ScrolledText(top_frame, height=3, 
                                                       bg='#3c3f41', fg='white', font=('Courier', 12))
        self.traffic_summary.pack(fill=tk.X)
        
        # Live traffic view with larger font
        self.traffic_text = scrolledtext.ScrolledText(self.traffic_tab, 
                                                    bg='#3c3f41', fg='white', font=('Courier', 14))
        self.traffic_text.pack(fill=tk.BOTH, expand=True)
        
        # Add a clear button
        clear_button = tk.Button(top_frame, text="Clear Display", 
                               command=lambda: self.traffic_text.delete(1.0, tk.END),
                               bg='#4b6eaf', fg='white')
        clear_button.pack(pady=5)

    def setup_content_tab(self):
        # Create paned window for URLs and Images
        paned = ttk.PanedWindow(self.content_tab, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # URL Frame
        url_frame = ttk.Frame(paned, style="Dark.TFrame")
        url_label = tk.Label(url_frame, text="HTTP/HTTPS URLs", 
                           bg='#2b2b2b', fg='white', font=('Arial', 12, 'bold'))
        url_label.pack(pady=5)
        
        # URL Treeview
        columns = ('Timestamp', 'Source', 'URL', 'Method', 'Content-Type')
        self.url_tree = ttk.Treeview(url_frame, columns=columns, show='headings')
        for col in columns:
            self.url_tree.heading(col, text=col)
            self.url_tree.column(col, width=100)
        self.url_tree.pack(fill=tk.BOTH, expand=True)
        
        # Image Frame
        image_frame = ttk.Frame(paned, style="Dark.TFrame")
        image_label = tk.Label(image_frame, text="Captured Images", 
                             bg='#2b2b2b', fg='white', font=('Arial', 12, 'bold'))
        image_label.pack(pady=5)
        
        # Image display area with scrollbar
        self.image_canvas = tk.Canvas(image_frame, bg='#3c3f41')
        scrollbar = ttk.Scrollbar(image_frame, orient=tk.HORIZONTAL, 
                                command=self.image_canvas.xview)
        self.image_canvas.configure(xscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.image_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Add frames to paned window
        paned.add(url_frame, weight=1)
        paned.add(image_frame, weight=1)

    def update_dashboard(self):
        while self.running:
            try:
                # Update device summary
                total_devices = len(self.devices)
                active_devices = sum(1 for d in self.devices.values() if d['status'] == 'Active')
                summary = f"Total Devices: {total_devices}\n"
                summary += f"Active Devices: {active_devices}\n"
                summary += f"Total Connections: {len(self.connection_history)}\n"
                
                self.device_summary.delete('1.0', tk.END)
                self.device_summary.insert(tk.END, summary)
                
                # Update traffic graph
                self.update_traffic_graph()
                
                # Update alerts
                self.update_alerts()
                
            except Exception as e:
                print(f"Error updating dashboard: {e}")
            
            time.sleep(2)

    def update_traffic_graph(self):
        try:
            self.ax_traffic.clear()
            devices = list(self.device_traffic.keys())[:5]  # Top 5 devices
            traffic = [self.device_traffic[d] for d in devices]
            
            self.ax_traffic.bar(devices, traffic, color='#4b6eaf')
            self.ax_traffic.set_title('Top Device Traffic', color='white')
            self.ax_traffic.tick_params(axis='x', colors='white')
            self.ax_traffic.tick_params(axis='y', colors='white')
            
            self.canvas_traffic.draw()
        except Exception as e:
            print(f"Error updating traffic graph: {e}")

    def update_alerts(self):
        try:
            self.alert_text.delete('1.0', tk.END)
            for alert in self.alerts[-10:]:  # Show last 10 alerts
                self.alert_text.insert(tk.END, f"{alert}\n")
        except Exception as e:
            print(f"Error updating alerts: {e}")

    def show_device_menu(self, event):
        try:
            item = self.devices_tree.identify_row(event.y)
            if item:
                self.devices_tree.selection_set(item)
                self.device_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"Error showing device menu: {e}")

    def set_device_category(self, category):
        try:
            selected = self.devices_tree.selection()[0]
            self.device_categories[selected] = category
            self.devices_tree.set(selected, 'Category', category)
        except Exception as e:
            print(f"Error setting device category: {e}")

    def resolve_hostname(self, ip):
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except:
            return ip

    def get_vendor_name(self, mac):
        try:
            mac = mac.upper()
            # Try different prefix lengths (first 6, 7, or 8 characters)
            for i in [6, 7, 8]:
                prefix = mac[:i]
                if prefix in self.mac_vendors:
                    return self.mac_vendors[prefix]
            
            # If no match found, return first part of MAC (manufacturer part)
            return f"Unknown ({mac[:8]})"
        except:
            return "Unknown Vendor"

    def get_service_name(self, port):
        return self.known_services.get(port, str(port))

    def scan_network(self):
        while self.running:
            try:
                gateways = netifaces.gateways()
                default_gateway = gateways['default'][netifaces.AF_INET][0]
                network = '.'.join(default_gateway.split('.')[:-1]) + '.0/24'

                arp_request = scapy.ARP(pdst=network)
                broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
                arp_request_broadcast = broadcast/arp_request
                answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                for element in answered_list:
                    ip = element[1].psrc
                    mac = element[1].hwsrc
                    hostname = self.resolve_hostname(ip)
                    vendor = self.get_vendor_name(mac)
                    
                    device_id = mac
                    if device_id not in self.devices:
                        category = self.guess_device_category(vendor, hostname)
                        self.devices[device_id] = {
                            'ip': ip,
                            'mac': mac,
                            'vendor': vendor,
                            'hostname': hostname,
                            'status': 'Active',
                            'category': category,
                            'activity': 'Just connected',
                            'last_seen': current_time
                        }
                        self.devices_tree.insert('', 'end', device_id,
                                               values=(category, ip, mac, vendor, hostname, 'Active', 
                                                      'Just connected', current_time))
                        self.add_alert(f"New device detected: {hostname} ({vendor})")
                    else:
                        activity = self.get_device_activity(device_id)
                        self.devices[device_id].update({
                            'last_seen': current_time,
                            'status': 'Active',
                            'activity': activity
                        })
                        self.devices_tree.item(device_id, values=(
                            self.devices[device_id]['category'],
                            ip, mac, vendor, hostname, 'Active', activity, current_time
                        ))

            except Exception as e:
                print(f"Error in network scan: {e}")
            
            time.sleep(5)

    def guess_device_category(self, vendor, hostname):
        vendor = vendor.lower()
        hostname = hostname.lower()
        
        categories = {
            'computer': ['pc', 'desktop', 'laptop', 'macbook', 'dell', 'hp', 'lenovo'],
            'phone': ['iphone', 'android', 'samsung', 'huawei', 'xiaomi'],
            'iot device': ['nest', 'ring', 'echo', 'alexa', 'smart'],
            'network equipment': ['router', 'switch', 'ap', 'cisco', 'netgear', 'tp-link'],
            'smart tv': ['tv', 'roku', 'chromecast', 'firestick'],
            'game console': ['playstation', 'xbox', 'nintendo', 'ps4', 'ps5']
        }
        
        for category, keywords in categories.items():
            if any(keyword in vendor or keyword in hostname for keyword in keywords):
                return category
        
        return "Unknown"

    def get_device_activity(self, device_id):
        if device_id in self.device_activity:
            activities = self.device_activity[device_id]
            if activities:
                return activities[-1]
        return "Idle"

    def add_alert(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.alerts.append(f"[{timestamp}] {message}")
        if len(self.alerts) > 100:  # Keep last 100 alerts
            self.alerts.pop(0)

    def monitor_connections(self):
        while self.running:
            try:
                for item in self.conn_tree.get_children():
                    self.conn_tree.delete(item)
                
                connections = psutil.net_connections(kind='inet')
                active_services = defaultdict(int)
                
                for conn in connections:
                    try:
                        if conn.laddr and conn.raddr:
                            local_ip = conn.laddr.ip
                            local_port = conn.laddr.port
                            remote_ip = conn.raddr.ip
                            remote_port = conn.raddr.port
                            status = conn.status
                            
                            try:
                                process = psutil.Process(conn.pid).name()
                            except:
                                process = "Unknown"
                            
                            remote_host = self.resolve_hostname(remote_ip)
                            service = self.get_service_name(remote_port)
                            active_services[service] += 1
                            
                            # Find local device name
                            local_device = "Unknown"
                            for device in self.devices.values():
                                if device['ip'] == local_ip:
                                    local_device = device['hostname']
                                    break
                            
                            conn_id = f"{local_ip}:{local_port}-{remote_ip}:{remote_port}"
                            
                            # Calculate connection duration
                            if conn_id not in self.connection_history:
                                self.connection_history[conn_id] = datetime.now()
                            duration = datetime.now() - self.connection_history[conn_id]
                            duration_str = str(duration).split('.')[0]
                            
                            self.conn_tree.insert('', 'end', conn_id,
                                                values=(local_device, local_ip, local_port,
                                                       f"{remote_host} ({remote_ip})",
                                                       service, status, process, duration_str))
                            
                            # Update device activity
                            for device_id, device in self.devices.items():
                                if device['ip'] == local_ip:
                                    activity = f"Connected to {service} on {remote_host}"
                                    self.device_activity[device_id].append(activity)
                                    if len(self.device_activity[device_id]) > 5:  # Keep last 5 activities
                                        self.device_activity[device_id].pop(0)
                    
                    except Exception as e:
                        continue
                
                # Update connection summary
                summary = "Active Services:\n"
                for service, count in active_services.items():
                    summary += f"{service}: {count} connections\n"
                self.conn_summary.delete('1.0', tk.END)
                self.conn_summary.insert(tk.END, summary)
                
            except Exception as e:
                print(f"Error in connection monitoring: {e}")
            
            time.sleep(2)

    def capture_traffic(self):
        def packet_callback(packet):
            try:
                if packet.haslayer(scapy.IP):
                    # Process HTTP/HTTPS and images
                    self.process_http_packet(packet)
                    
                    # Continue with regular packet processing
                    src_ip = packet[scapy.IP].src
                    dst_ip = packet[scapy.IP].dst
                    protocol = packet[scapy.IP].proto
                    length = len(packet)
                    
                    # Update device traffic statistics
                    for device_id, device in self.devices.items():
                        if device['ip'] in [src_ip, dst_ip]:
                            self.device_traffic[device_id] += length
                    
                    src_host = self.resolve_hostname(src_ip)
                    dst_host = self.resolve_hostname(dst_ip)
                    
                    proto_name = "TCP" if protocol == 6 else "UDP" if protocol == 17 else str(protocol)
                    
                    # Get service name if available
                    service = ""
                    if packet.haslayer(scapy.TCP):
                        sport, dport = packet[scapy.TCP].sport, packet[scapy.TCP].dport
                        service = self.get_service_name(dport)
                    elif packet.haslayer(scapy.UDP):
                        sport, dport = packet[scapy.UDP].sport, packet[scapy.UDP].dport
                        service = self.get_service_name(dport)
                    
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    packet_info = f"[{timestamp}] {src_host} ({src_ip}) → {dst_host} ({dst_ip}) | {proto_name}"
                    if service:
                        packet_info += f" | {service}"
                    packet_info += f" | {length} bytes\n"
                    
                    self.traffic_text.insert(tk.END, packet_info)
                    self.traffic_text.see(tk.END)
                    
                    if float(self.traffic_text.index('end-1c')) > 1000:
                        self.traffic_text.delete('1.0', '2.0')
                    
                    # Update traffic summary
                    self.update_traffic_summary()
            except Exception as e:
                print(f"Error in packet callback: {e}")

        # Load required layers
        scapy.load_layer('http')
        scapy.load_layer('tls')
        
        # Start packet capture with the defined callback
        scapy.sniff(prn=packet_callback, store=False, filter="ip")

    def update_traffic_summary(self):
        try:
            total_traffic = sum(self.device_traffic.values())
            summary = f"Total Network Traffic: {total_traffic/1024:.2f} KB\n"
            summary += "Top Talkers:\n"
            
            # Sort devices by traffic
            sorted_devices = sorted(self.device_traffic.items(), key=lambda x: x[1], reverse=True)[:5]
            for device_id, traffic in sorted_devices:
                if device_id in self.devices:
                    device = self.devices[device_id]
                    summary += f"{device['hostname']}: {traffic/1024:.2f} KB\n"
            
            self.traffic_summary.delete('1.0', tk.END)
            self.traffic_summary.insert(tk.END, summary)
            
        except Exception as e:
            print(f"Error updating traffic summary: {e}")

    def on_closing(self):
        self.running = False
        # Clean up cache directory
        try:
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                os.remove(file_path)
            os.rmdir(self.cache_dir)
        except:
            pass
        self.destroy()

    def load_mac_vendors(self):
        try:
            # Try to download the latest MAC vendor database
            response = requests.get('https://raw.githubusercontent.com/wireshark/wireshark/master/manuf')
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    if line and not line.startswith('#'):
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            mac_prefix = parts[0].strip().upper()
                            vendor = parts[1].strip()
                            self.mac_vendors[mac_prefix] = vendor
        except:
            # Fallback to basic vendor identification
            self.mac_vendors = {
                'DC:A6:32': 'Raspberry Pi',
                '00:50:56': 'VMware',
                'AC:DE:48': 'Private',
                '00:0C:29': 'VMware',
                '00:1A:11': 'Google',
                '00:17:88': 'Philips',
                '18:B4:30': 'Nest Labs',
                'B8:27:EB': 'Raspberry Pi',
                '00:25:00': 'Apple',
                '58:55:CA': 'Apple',
                'BC:83:85': 'Microsoft',
                '00:15:5D': 'Microsoft',
            }

    def process_http_packet(self, packet):
        """Process HTTP and HTTPS packets for detailed analysis"""
        try:
            if packet.haslayer(http.HTTPRequest):
                src_ip = packet[scapy.IP].src
                http_layer = packet[http.HTTPRequest]
                
                # Get the full URL and path
                host = http_layer.Host.decode() if http_layer.Host else ""
                path = http_layer.Path.decode() if http_layer.Path else ""
                
                # Find device info
                device_name = "Unknown Device"
                device_id = None
                for d_id, device in self.devices.items():
                    if device['ip'] == src_ip:
                        device_name = device['hostname']
                        device_id = d_id
                        break
                
                # Format timestamp
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                # Simplify the URL display
                url = f"{host}{path}"
                activity = "Unknown Activity"
                
                # Categorize the activity
                if 'youtube' in url:
                    if 'watch?v=' in url:
                        video_id = url.split('watch?v=')[1].split('&')[0]
                        activity = f"🎥 Watching YouTube Video ({video_id})"
                    else:
                        activity = "🎥 Browsing YouTube"
                elif 'facebook' in url:
                    if 'messages' in url:
                        activity = "💬 Using Facebook Messenger"
                    elif 'photo' in url or 'image' in url:
                        activity = "📸 Viewing Facebook Photos"
                    else:
                        activity = "👥 Browsing Facebook"
                elif 'netflix' in url:
                    activity = "🎬 Watching Netflix"
                elif 'spotify' in url:
                    activity = "🎵 Listening to Music"
                elif 'amazon' in url:
                    if 'product' in url:
                        activity = "🛒 Shopping on Amazon"
                    else:
                        activity = "🛍️ Browsing Amazon"
                elif 'google' in url:
                    if 'mail' in url:
                        activity = "📧 Checking Gmail"
                    elif 'maps' in url:
                        activity = "🗺️ Using Google Maps"
                    else:
                        activity = "🔍 Searching on Google"
                else:
                    activity = f"🌐 Browsing {host}"
                
                # Create simple activity message
                activity_msg = f"[{timestamp}] {device_name}: {activity}\n"
                
                # Update traffic text
                self.traffic_text.insert(tk.END, activity_msg)
                self.traffic_text.see(tk.END)
                
                # Update device activity
                if device_id:
                    self.devices[device_id]['activity'] = activity
                    self.device_activity[device_id].append(activity)
                    # Update device in tree view
                    self.devices_tree.item(device_id, values=(
                        self.devices[device_id]['category'],
                        self.devices[device_id]['ip'],
                        self.devices[device_id]['mac'],
                        self.devices[device_id]['vendor'],
                        self.devices[device_id]['hostname'],
                        'Active',
                        activity,
                        timestamp
                    ))
                
            elif packet.haslayer(TLS) and packet.haslayer(scapy.TCP):
                if packet[scapy.TCP].dport == 443:
                    src_ip = packet[scapy.IP].src
                    sni = self.extract_sni(packet)
                    if sni:
                        # Find device info
                        device_name = "Unknown Device"
                        device_id = None
                        for d_id, device in self.devices.items():
                            if device['ip'] == src_ip:
                                device_name = device['hostname']
                                device_id = d_id
                                break
                        
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        
                        # Categorize HTTPS activity
                        activity = "Unknown HTTPS Activity"
                        if 'netflix' in sni:
                            activity = "🎬 Watching Netflix"
                        elif 'youtube' in sni:
                            activity = "🎥 Using YouTube"
                        elif 'spotify' in sni:
                            activity = "🎵 Using Spotify"
                        elif 'facebook' in sni:
                            activity = "👥 Using Facebook"
                        elif 'instagram' in sni:
                            activity = "📸 Using Instagram"
                        elif 'twitter' in sni:
                            activity = "🐦 Using Twitter"
                        elif 'tiktok' in sni:
                            activity = "📱 Using TikTok"
                        elif 'amazon' in sni:
                            activity = "🛒 Shopping on Amazon"
                        elif 'netflix' in sni:
                            activity = "🎬 Streaming Netflix"
                        elif 'disney' in sni:
                            activity = "🎬 Streaming Disney+"
                        elif 'hulu' in sni:
                            activity = "🎬 Streaming Hulu"
                        elif 'zoom' in sni:
                            activity = "🎥 In Zoom Meeting"
                        elif 'teams' in sni:
                            activity = "👥 In Teams Meeting"
                        elif 'slack' in sni:
                            activity = "💬 Using Slack"
                        elif 'discord' in sni:
                            activity = "🎮 Using Discord"
                        elif 'whatsapp' in sni:
                            activity = "💬 Using WhatsApp"
                        elif 'github' in sni:
                            activity = "💻 Using GitHub"
                        else:
                            activity = f"🔒 Accessing {sni}"
                        
                        activity_msg = f"[{timestamp}] {device_name}: {activity}\n"
                        self.traffic_text.insert(tk.END, activity_msg)
                        self.traffic_text.see(tk.END)
                        
                        # Update device activity
                        if device_id:
                            self.devices[device_id]['activity'] = activity
                            self.device_activity[device_id].append(activity)
                            # Update device in tree view
                            self.devices_tree.item(device_id, values=(
                                self.devices[device_id]['category'],
                                self.devices[device_id]['ip'],
                                self.devices[device_id]['mac'],
                                self.devices[device_id]['vendor'],
                                self.devices[device_id]['hostname'],
                                'Active',
                                activity,
                                timestamp
                            ))
        
        except Exception as e:
            print(f"Error processing HTTP packet: {e}")

    def extract_sni(self, packet):
        """Extract Server Name Indication from TLS packet"""
        try:
            if packet.haslayer(TLS):
                if packet[TLS].type == 1:  # Client Hello
                    for ext in packet[TLS].extensions:
                        if ext.type == 0:  # SNI extension
                            return ext.server_names[0].decode()
        except:
            pass
        return None

if __name__ == "__main__":
    app = NetworkMonitor()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop() 