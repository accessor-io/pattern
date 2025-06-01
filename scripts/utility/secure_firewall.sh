#!/bin/bash

# Check if script is run as root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Load required modules
modprobe ip_conntrack
modprobe ip_conntrack_ftp
modprobe ip_nat_ftp
modprobe nf_conntrack
modprobe nfnetlink
modprobe nf_conntrack_netlink

# Create custom chains
iptables -N TCP
iptables -N UDP
iptables -N LOG_AND_DROP
iptables -N MONITORING

# Flush existing rules and set default policies
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X

# Set default chain policies to DROP
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Create LOG_AND_DROP chain rules
iptables -A LOG_AND_DROP -j LOG --log-prefix "IPTables-Dropped: " --log-level 4
iptables -A LOG_AND_DROP -j DROP

# Allow loopback interface
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Create MONITORING chain for network analysis
iptables -A MONITORING -j ACCEPT
iptables -A FORWARD -j MONITORING
iptables -A INPUT -j MONITORING

# Enable promiscuous mode on all interfaces
for interface in $(ip -o link show | awk -F': ' '{print $2}'); do
    ip link set dev $interface promisc on
done

# Allow established and related connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow router communication
iptables -A INPUT -s 10.1.10.1 -j ACCEPT
iptables -A OUTPUT -d 10.1.10.1 -j ACCEPT

# Allow all local network traffic for monitoring
iptables -A INPUT -s 192.168.0.0/16 -j ACCEPT
iptables -A INPUT -s 172.16.0.0/12 -j ACCEPT
iptables -A INPUT -s 10.0.0.0/8 -j ACCEPT

# Allow ARP for network discovery
iptables -A INPUT -p arp -j ACCEPT
iptables -A OUTPUT -p arp -j ACCEPT

# Allow DHCP
iptables -A INPUT -p udp --dport 67:68 --sport 67:68 -j ACCEPT

# Allow specific monitoring protocols
iptables -A INPUT -p tcp --dport 80 -j ACCEPT   # HTTP
iptables -A INPUT -p tcp --dport 443 -j ACCEPT  # HTTPS
iptables -A INPUT -p udp --dport 53 -j ACCEPT   # DNS
iptables -A INPUT -p icmp -j ACCEPT             # ICMP (ping)

# Allow all traffic monitoring but log it
iptables -A INPUT -m state --state NEW -j LOG --log-prefix "Network-Monitor: " --log-level 4

# Allow specific outbound services with state tracking
iptables -A OUTPUT -p tcp --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT  # HTTP
iptables -A OUTPUT -p tcp --dport 443 -m state --state NEW,ESTABLISHED -j ACCEPT # HTTPS
iptables -A OUTPUT -p tcp --dport 53 -m state --state NEW,ESTABLISHED -j ACCEPT  # DNS
iptables -A OUTPUT -p udp --dport 53 -m state --state NEW,ESTABLISHED -j ACCEPT  # DNS

# Save rules
iptables-save > /etc/iptables/rules.v4

# Enable system logging for iptables
if ! grep -q "kern.* /var/log/iptables.log" /etc/syslog.conf; then
    echo "kern.* /var/log/iptables.log" >> /etc/syslog.conf
    touch /var/log/iptables.log
    chmod 600 /var/log/iptables.log
fi

echo "Enhanced firewall rules have been applied and saved."
echo "Network monitoring is now enabled."