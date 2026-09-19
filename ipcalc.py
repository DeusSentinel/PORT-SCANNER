import socket
import argparse
port = 0
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
            target = s.connect_ex((args.target, i))
        except socket.timeout:
            print(f"Error! on port {i}")

        if target == 0 :
            print(f"Port {i} is open.")
        print(target)
        
    
