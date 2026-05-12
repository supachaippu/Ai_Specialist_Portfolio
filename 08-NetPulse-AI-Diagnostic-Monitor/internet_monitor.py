import subprocess
import time
import csv
import os
import socket
from datetime import datetime

# Configuration
LOG_FILE = "internet_logs.csv"
CHECK_INTERVAL = 5  # Seconds between checks
TARGET_PUBLIC = "8.8.8.8"  # Google DNS (Internet check)
TARGET_DNS = "google.com"  # Name resolution check

def get_gateway():
    """Find the local router gateway IP."""
    try:
        output = subprocess.check_output(["netstat", "-rn"], text=True)
        for line in output.splitlines():
            if "default" in line:
                parts = line.split()
                if len(parts) > 1:
                    return parts[1]
    except Exception:
        pass
    return "192.168.1.1"  # Default assumption if fails

def get_wifi_info():
    """Get macOS WiFi signal info (Try airport first, then wdutil)."""
    # 1. Try legacy airport tool
    try:
        cmd = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I"
        output = subprocess.check_output(cmd, shell=True, text=True)
        info = {}
        for line in output.splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                info[key.strip()] = val.strip()
        
        if info:
            return {
                "ssid": info.get("SSID", "N/A"),
                "rssi": info.get("agrCtlRSSI", "0"),
                "noise": info.get("agrCtlNoise", "0"),
                "rate": info.get("lastTxRate", "0")
            }
    except Exception:
        pass

    # 2. Try modern wdutil (for Sonoma+)
    try:
        cmd = "wdutil info"
        output = subprocess.check_output(cmd, shell=True, text=True)
        info = {}
        for line in output.splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                info[key.strip()] = val.strip()
        
        return {
            "ssid": info.get("SSID", "N/A"),
            "rssi": info.get("RSSI", "0"),
            "noise": "0",  # wdutil might not show noise clearly
            "rate": "0" 
        }
    except Exception:
        return {"ssid": "N/A", "rssi": "0", "noise": "0", "rate": "0"}

def ping(host):
    """Ping a host and return success status and latency."""
    try:
        start = time.time()
        # -t 1 sends 1 ping, -W 1000 waits 1 second
        subprocess.check_output(["ping", "-c", "1", "-W", "1000", host], stderr=subprocess.STDOUT)
        latency = (time.time() - start) * 1000
        return True, round(latency, 2)
    except subprocess.CalledProcessError:
        return False, 0

def check_dns(host):
    """Check if DNS resolution is working."""
    try:
        socket.gethostbyname(host)
        return True
    except socket.error:
        return False

def setup_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Public_IP_Ping", "Gateway_Ping", "DNS_Check", "Latency", "SSID", "RSSI", "Noise", "Rate", "Status"])

def log_status(data):
    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)

def main():
    gateway = get_gateway()
    print(f"Internet Monitoring Started...")
    print(f"Logging to: {os.path.abspath(LOG_FILE)}")
    print(f"Gateway: {gateway} | Public: {TARGET_PUBLIC}")
    print("Press Ctrl+C to stop.")
    
    setup_log()
    
    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            public_ok, latency = ping(TARGET_PUBLIC)
            gateway_ok, _ = ping(gateway)
            dns_ok = check_dns(TARGET_DNS)
            wifi = get_wifi_info()
            
            # Diagnose status
            status = "Online"
            if not public_ok:
                if not gateway_ok:
                    status = "Lost Router Connection (Check WiFi/Cable)"
                elif not dns_ok:
                    status = "DNS Issue (ISP side)"
                else:
                    status = "ISP/Cloud Link Down"
            
            # Log
            log_status([
                timestamp, 
                "OK" if public_ok else "FAIL", 
                "OK" if gateway_ok else "FAIL", 
                "OK" if dns_ok else "FAIL", 
                latency, 
                wifi['ssid'], 
                wifi['rssi'], 
                wifi['noise'], 
                wifi['rate'],
                status
            ])
            
            print(f"[{timestamp}] {status} | Latency: {latency}ms | RSSI: {wifi['rssi']} | SSID: {wifi['ssid']}")
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()
