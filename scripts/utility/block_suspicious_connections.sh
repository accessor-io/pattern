#!/bin/bash

# Block Suspicious Connections Script
# Generated from security analysis
# Date: $(date)

echo "Starting security blocking procedure..."

# Block AWS IPs
echo "Blocking suspicious AWS IPs..."
sudo iptables -A INPUT -s 34.235.241.112 -j DROP
sudo iptables -A OUTPUT -d 34.235.241.112 -j DROP
sudo iptables -A INPUT -s 52.205.148.217 -j DROP
sudo iptables -A OUTPUT -d 52.205.148.217 -j DROP
sudo iptables -A INPUT -s 34.234.80.161 -j DROP
sudo iptables -A OUTPUT -d 34.234.80.161 -j DROP
sudo iptables -A INPUT -s 3.211.136.73 -j DROP
sudo iptables -A OUTPUT -d 3.211.136.73 -j DROP

# Block Suspicious Ports
echo "Blocking suspicious ports..."
sudo iptables -A INPUT -p tcp --dport 9050 -j DROP
sudo iptables -A INPUT -p tcp --dport 9040 -j DROP
sudo iptables -A INPUT -p tcp --dport 8080 -j DROP
sudo iptables -A INPUT -p tcp --dport 9200 -j DROP
sudo iptables -A INPUT -p tcp --dport 9300 -j DROP

# Stop and Disable Services
echo "Stopping suspicious services..."
sudo systemctl stop elasticsearch
sudo systemctl disable elasticsearch
sudo systemctl stop tor
sudo systemctl disable tor
sudo systemctl stop tinyproxy
sudo systemctl disable tinyproxy

# Remove Cron Jobs
echo "Removing suspicious cron jobs..."
sudo rm -f /etc/cron.weekly/tor

# Save IPTables Rules
echo "Saving firewall rules..."
sudo netfilter-persistent save
sudo netfilter-persistent reload

# Verify Blocks
echo "Verifying blocks..."
sudo iptables -L
sudo systemctl status elasticsearch
sudo systemctl status tor
sudo systemctl status tinyproxy

echo "Blocking procedure completed."
echo "Please review the output above for any errors."

# Log the execution
echo "Script executed on $(date)" >> /var/log/security_blocks.log 