#!/bin/bash

# Network Connection Monitoring Script
# Generated from security analysis
# Date: $(date)

LOG_FILE="/var/log/connection_monitor.log"
ALERT_FILE="/var/log/connection_alerts.log"

echo "Starting network connection monitoring..."
echo "Monitoring started at $(date)" >> "$LOG_FILE"

# Function to log alerts
log_alert() {
    echo "[$(date)] ALERT: $1" >> "$ALERT_FILE"
    echo "[$(date)] ALERT: $1"
}

# Monitor suspicious ports
monitor_ports() {
    netstat -tuln | grep -E ":(9050|9040|8080|9200|9300)" > /dev/null
    if [ $? -eq 0 ]; then
        log_alert "Suspicious ports detected:"
        netstat -tuln | grep -E ":(9050|9040|8080|9200|9300)" >> "$ALERT_FILE"
    fi
}

# Monitor AWS connections
monitor_aws() {
    netstat -tun | grep -E "34.235.241.112|52.205.148.217|34.234.80.161|3.211.136.73" > /dev/null
    if [ $? -eq 0 ]; then
        log_alert "AWS connections detected:"
        netstat -tun | grep -E "34.235.241.112|52.205.148.217|34.234.80.161|3.211.136.73" >> "$ALERT_FILE"
    fi
}

# Monitor suspicious services
monitor_services() {
    for service in elasticsearch tor tinyproxy; do
        systemctl is-active --quiet $service
        if [ $? -eq 0 ]; then
            log_alert "Suspicious service $service is running"
        fi
    done
}

# Monitor new connections
monitor_connections() {
    netstat -tun | grep ESTABLISHED > /tmp/current_connections
    if [ -f /tmp/previous_connections ]; then
        diff /tmp/previous_connections /tmp/current_connections | grep ">" | while read line; do
            log_alert "New connection detected: $line"
        done
    fi
    mv /tmp/current_connections /tmp/previous_connections
}

# Monitor system load
monitor_load() {
    load=$(uptime | awk -F'load average:' '{ print $2 }' | cut -d, -f1)
    if (( $(echo "$load > 5.0" | bc -l) )); then
        log_alert "High system load detected: $load"
    fi
}

# Monitor memory usage
monitor_memory() {
    memory_usage=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
    if (( $(echo "$memory_usage > 90.0" | bc -l) )); then
        log_alert "High memory usage detected: ${memory_usage}%"
    fi
}

# Main monitoring loop
while true; do
    echo "Running checks at $(date)" >> "$LOG_FILE"
    
    monitor_ports
    monitor_aws
    monitor_services
    monitor_connections
    monitor_load
    monitor_memory
    
    # Check for suspicious processes
    ps aux | grep -i "elasticsearch\|tor\|tinyproxy" | grep -v grep >> "$LOG_FILE"
    
    # Log current connections
    echo "Current connections:" >> "$LOG_FILE"
    netstat -tun | grep ESTABLISHED >> "$LOG_FILE"
    
    # Add separator in log
    echo "----------------------------------------" >> "$LOG_FILE"
    
    # Wait before next check
    sleep 60
done 