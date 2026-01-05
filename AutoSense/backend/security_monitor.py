import psutil
import socket
import subprocess

def check_firewall_status():
    try:
        # Using netsh to check firewall
        output = subprocess.check_output("netsh advfirewall show allprofiles state", shell=True).decode()
        if "ON" in output:
            return True
        return False
    except:
        return False # Assume risky if check fails

def enable_firewall():
    try:
        subprocess.run("netsh advfirewall set allprofiles state on", shell=True, check=True)
        return True
    except:
        return False

import time

_cache = {
    "ports": [],
    "last_scan": 0
}

def check_open_ports():
    global _cache
    # Cache for 60 seconds to improve performance
    if time.time() - _cache['last_scan'] < 60:
        return _cache['ports']

    open_ports = []
    # Scan common risky ports
    risky_ports = {
        21: "FTP (File Transfer)",
        23: "Telnet (Unencrypted)",
        3389: "RDP (Remote Desktop)",
        445: "SMB (File Sharing)",
        80: "HTTP (Unencrypted Web)"
    }
    
    # Use psutil to find listening ports
    connections = psutil.net_connections(kind='inet')
    for conn in connections:
        if conn.status == 'LISTEN':
            port = conn.laddr.port
            if port in risky_ports:
                open_ports.append({
                    "port": port,
                    "service": risky_ports[port],
                    "risk": "HIGH"
                })
            elif port < 1024:
                open_ports.append({
                    "port": port,
                    "service": "System Service",
                    "risk": "MEDIUM"
                })
    
    # Deduplicate
    unique_ports = list({p['port']: p for p in open_ports}.values())
    
    _cache['ports'] = unique_ports
    _cache['last_scan'] = time.time()
    
    return unique_ports
