import socket
import argparse
import errno
import threading
import tabulate
import math

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

    #Adds positional arguments 
    parser = argparse.ArgumentParser(prog="TARGET", description= "Selects target IPV4 address", epilog= "Accepts target IP address")
    parser.add_argument("target", type= str, help= "Enter the target IP address")
    parser.add_argument("start_port", type= int, help="Enter the beginning of the range of s")
    parser.add_argument("end_port", type= int, help= "Enter the end of the range of s.")
    parser.add_argument("time", type= float, help= "Set the timeout value")
    args = parser.parse_args()

    #Input validation to accept valid port numbers between 1 and 65535
    # It also ensures the timeout value is a positive non-zero number
    if args.target.replace(".", "").isdigit() == False:
        raise ValueError("Invalid target. Must be integer values.")
 
    if not( 65535 > args.start_port > 0):
        raise ValueError("Invlaid starting  number. Starting port must be between 1 and 65535")
    elif not (0 < args.end_port < 65536):
        raise ValueError("Invalid end . number. Ending port must be between 1 and 65535.")
    elif args.start_port > args.end_port:
        raise ValueError("Invalid starting  number. Must be less than end .")
    elif not math.isfinite(args.time) or args.time <= 0:
        raise ValueError("Invalid timeout value. Must be a positive non-zero number.")
    
    #Returns the CLI positional arguments
    return args


def TCP_Scan (args):
    results_tcp = []
    #For loop that iterates over each port in the given range
    for i in range(args.start_port, (args.end_port + 1)):   

        #Creates a TCP socket that usees IPV4 IP addresses
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            #Set a timeout value that jumps to next port if the port doesn't respond within the specified time 
            s.settimeout(args.time)

            #Establishes a TCP connection to given IP address on the given port
            tcp_target = s.connect_ex((args.target, i))

            #Handles the results_tcp that the connection may return
            # IF the connection is successful, connect_ex will return 0.
            if tcp_target == 0 :

                #If it is a common port, it is then appended to the summary table with the appropriate Service
                #If it is uncommon, it is still appended to the summary table but with the service "Unknown Service"
                data_tcp = [f"{i}", "Open", tcp_ports.get(i, "Unknown Service")]
                results_tcp.append(data_tcp)

            #If the port is closed, the "errno.ECONNREFUSED" will be returned and the error message will be printed.

            elif tcp_target == errno.ECONNREFUSED:
                data_tcp = [f"{i}", "Closed", tcp_ports.get(i, "Unknown Service")]
                results_tcp.append(data_tcp)

            #If the port is has not responded in the given time it is assumed to be filtered and,
            # the "errno.ETIMEOUT" will be returned and the error message will be printed.
            elif tcp_target == errno.ETIMEDOUT:
                data_tcp = [f"{i}", "Filtered", tcp_ports.get(i, "Unknown Service")]
                results_tcp.append(data_tcp)
            else:
                data_tcp = [f"{i}", "Unknown", tcp_ports.get(i, "Unknown Service")]
                results_tcp.append(data_tcp)
    return results_tcp

def run_tcp(args, results):
    results["tcp"] = TCP_Scan(args)

def run_udp(args, results):
    results["udp"] = UDP_Scan(args)
    
              
        
def UDP_Scan(args):
    results_udp = []
    #For loop that iterates over each port in the given range
    for i in range(args.start_port, (args.end_port + 1)):
        
        #Creates a UDP socket that uses IPV4 IP address
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as u:

            #Set a timeout value that jumps to next port if the port doesn't respond within the specified time 
            u.settimeout(args.time)
            try:

                #Sends a message to the "server" using the given IP and port number
                u.sendto(b"hello", (args.target, i))

                #Collects the "response" [up to 1024 bytes] from the "server" and the IPV4 address
                data, address = u.recvfrom(1024)

                #If it is a common port, it is then added to the summary table with the appropriate Service
                #If it is uncommon, it is still added to the summary table but with the service "Unknown Service"
                data_udp = [f"{i}", "Open", udp_ports.get(i, "Unknown Service")]
                results_udp.append(data_udp)
                
            # The recvfrom() function will return a "ConnectionRefusedError" if the port is closed.
            except ConnectionRefusedError:
                    data_udp = [f"{i}", "Closed", udp_ports.get(i, "Unknown Service")]
                    results_udp.append(data_udp)
            # If the "server" does not respond in the specified time, it is assumed to be filtered.
            except socket.timeout:
                data_udp = [f"{i}", "No Response", udp_ports.get(i, "Unknown Service")]
                results_udp.append(data_udp)
    return results_udp
            
    
#Function that prints the summary
def summary_report(results_udp, results_tcp):
    udp_table = tabulate.tabulate(
    results_udp,
    headers = ["Port", "State", "Service"],
    tablefmt = "grid"

)
    tcp_table = tabulate.tabulate(
        results_tcp,
        headers = ["Port", "State", "Service"],
        tablefmt = "grid"
)
    print(udp_table)
    print(tcp_table)

        

if __name__ == "__main__":
    results = {}
    #Stores the args return from the initialize() function
    args = initialize()

    #Creates a thread for the TCP_Scan function, with the parameters
    tcp = threading.Thread(target=run_tcp, args=(args,results))

    #Creates a thread for the TCP_Scan function, with the parameters
    udp = threading.Thread(target=run_udp, args=(args, results))  

    #Starts the thread
    tcp.start()
    udp.start()

    #Ensures that the main thread does not continue until the two threads are finished.
    tcp.join()
    udp.join()
    
    #Prints the summary
    summary_report(results["udp"], results["tcp"])
    print("\nJOB DONE.")
