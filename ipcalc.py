import socket
import argparse
import errno

parser = argparse.ArgumentParser(prog="TARGETPORT", description= "Selects target IPV4 address", epilog= "Accepts target IP address")
parser.add_argument("target", type= str, help= "Enter the target IP address")
parser.add_argument("start_port", type= int, help="Enter the beginning of the range of ports")
parser.add_argument("end_port", type= int, help= "Enter the end of the range of ports. Not included.")
parser.add_argument("time", type= float, help= "Set the timeout value")
args = parser.parse_args()

for i in range(args.start_port, args.end_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(args.time)
        try:
            tcp_target = s.connect_ex((args.target, i))
            if tcp_target == 0 :
                print(f"Port {i} is open.")
            elif tcp_target == errno.ECONNREFUSED:
                print(f"Port {i} is closed.")
            print(tcp_target)
        except socket.timeout:
            print(f"Port {i} is filtered.")
 
        
    
for i in range(args.start_port, args.end_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as u:
        u.settimeout(args.time)
        u.sendto(b"hello", (args.target, i))
        try:
            data, address = u.recvfrom(1024)
            print(f"Port {i} is open")
        except ConnectionRefusedError:
                print(f"Port {i} is closed.")
        except socket.timeout:
            print(f"Port {i} is filtered.")
        
        