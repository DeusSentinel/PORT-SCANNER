import socket
import argparse
import threading

def scanner():
    parser = argparse.ArgumentParser(prog="TARGETPORT", description= "Port Scanner that accepts a target IP and a range of ports to scan using TCP protocol.", epilog= "Accepts target IP address")
    parser.add_argument("target", type= str, help= "Enter the target IP address")
    parser.add_argument("start_port", type= int, help="Enter the beginning of the range of ports")
    parser.add_argument("end_port", type= int, help= "Enter the end of the range of ports. Not included.")
    parser.add_argument("time", type= float, help= "Set the timeout value")
    args = parser.parse_args()

    known_services = {
        "port" : "service",
        "80" : "HTTP",
        "443" : "HTTPS",
        "20": "FTP",
        "21" : "TCP",
        "22" : "SSH",
        "23" : "Telnet",
        "25" : "SMTP",
        "53" : "DNS",
        "143" : "IMAP4",
        "110" : "POP3",
    }
    scan(args)
    return known_services


def scan(args):
    for i in range(args.start_port, args.end_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(args.time)
            while True:
                try:
                    result = s.connect_ex((args.target, i))
                    break
                except ValueError:
                    print("Target must be a string.")
                except socket.timeout:
                    print(f"Error! on port {i}")
`
        if result == 0 :
            print(f"Port {i} is open.")
            print(result)

        for i in range(args.end_port + 1):
            for i in range

if __name__ == "__main__":
    t = threading.Thread(target=scanner, args=[])
    t.start()

    

