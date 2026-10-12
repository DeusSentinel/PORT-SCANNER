import socket
import argparse
import errno
import threading
udp_summary = []
tcp_summary = []

# ==========================================
# TCP PORT SERVICES DICTIONARY
# ==========================================
tcp_ports = {
    21:   "FTP (File Transfer Protocol - Control)",
    22:   "SSH (Secure Shell / Secure FTP)",
    23:   "Telnet (Unencrypted Remote Terminal)",
    25:   "SMTP (Simple Mail Transfer Protocol - Email Routing)",
    53:   "DNS (Domain Name System - Zone Transfers/Large Queries)",
    80:   "HTTP (Hypertext Transfer Protocol - Unencrypted Web)",
    110:  "POP3 (Post Office Protocol v3 - Email Retrieval)",
    139:  "NetBIOS Session Service",
    143:  "IMAP (Internet Message Access Protocol - Email Syncing)",
    389:  "LDAP (Lightweight Directory Access Protocol)",
    443:  "HTTPS (HTTP Secure - Encrypted Web)",
    445:  "SMB (Server Message Block - Windows File Sharing)",
    1433: "MSSQL (Microsoft SQL Server Database)",
    3306: "MySQL (MySQL Database)",
    3389: "RDP (Remote Desktop Protocol - Core Graphical Stream)",
    5432: "PostgreSQL (PostgreSQL Database)",
    8080: "HTTP-Alt (Common HTTP Alternative / Web Proxy)"
}

# ==========================================
# UDP PORT SERVICES DICTIONARY
# ==========================================
udp_ports = {
    53:   "DNS (Domain Name System - Standard Queries)",
    67:   "DHCP Server (Dynamic Host Configuration Protocol)",
    68:   "DHCP Client (Dynamic Host Configuration Protocol)",
    69:   "TFTP (Trivial File Transfer Protocol)",
    123:  "NTP (Network Time Protocol - Time Synchronization)",
    137:  "NetBIOS Name Service",
    138:  "NetBIOS Datagram Service",
    161:  "SNMP (Simple Network Management Protocol - Device Polling)",
    162:  "SNMP Trap (Simple Network Management Protocol - Event Traps)",
    389:  "LDAP (Lightweight Directory Access Protocol - Connectionless)",
    500:  "ISAKMP / IKE (IPsec VPN Key Exchange)",
    514:  "Syslog (System Logging Protocol)",
    1900: "SSDP (Simple Service Discovery Protocol - UPnP Plug & Play)",
    3389: "RDP (Remote Desktop Protocol - Video/Audio Extensions)",
    5353: "mDNS (Multicast DNS - Local Network Device Discovery)"
}


def initialize():
    parser = argparse.ArgumentParser(prog="TARGET", description= "Selects target IPV4 address", epilog= "Accepts target IP address")
    parser.add_argument("target", type= str, help= "Enter the target IP address")
    parser.add_argument("start_port", type= int, help="Enter the beginning of the range of s")
    parser.add_argument("end_port", type= int, help= "Enter the end of the range of s.")
    parser.add_argument("time", type= float, help= "Set the timeout value")
    args = parser.parse_args()

    while True:
        if args.start_port > args.end_port:
            raise ValueError("Invalid starting  number. Must be less than end .")
        elif args.start_port <= 0:
            raise ValueError("Invlaid starting  number. Must be greater 0.")
        elif args.end_port > 65535:
            raise ValueError("Invalid end . number. Valid s end at 65535.")
        elif args.time <= 0:
            raise ValueError("Invalid timeout value. Must be a positive non-zero number.")
        break
    return args

def TCP_Scan (args):
    for i in range(args.start_port, (args.end_port + 1)):   
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(args.time)
            tcp_target = s.connect_ex((args.target, i))
            if tcp_target == 0 :
                tcp_summary.append((i, tcp_ports.get(args.start_port, "Unknown Service")))
            elif tcp_target == errno.ECONNREFUSED:
                print(f" {i} is closed.")
            elif tcp_target == errno.ETIMEDOUT:
                print(f" {i} is filtered.")

        
def UDP_Scan(args):
    for i in range(args.start_port, (args.end_port + 1)):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as u:
            u.settimeout(args.time)
            u.sendto(b"hello", (args.target, i))
            try:
                data, address = u.recvfrom(1024)
                udp_summary.append((i, udp_ports.get(i, "Unknown Service")))
            except ConnectionRefusedError:
                    print(f" {i} is closed.")
            except socket.timeout:
                print(f"No respone.  {i} may be filtered.")
            
    

def summary_report():
    print(udp_summary)
    print(tcp_summary)

        

if __name__ == "__main__":
    args = initialize()
    tcp = threading.Thread(target=TCP_Scan, args=(args,))
    udp = threading.Thread(target=UDP_Scan, args=(args,))  
    tcp.start()
    udp.start()
    tcp.join()
    udp.join()
    summary_report()
    print("\nJOB DONE.")
