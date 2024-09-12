import socket
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Send UDP packet with data")
parser.add_argument('--data', type=str, required=True, help="Data to send in UDP packet")
args = parser.parse_args()

# Define the UDP target IP and port
UDP_IP = "server-ip-or-fqdn"  # Replace with your destination IP
UDP_PORT = 12345          # Replace with your destination port

# The data to be sent is passed as a command-line argument
message = args.data

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send the data as a UDP packet
sock.sendto(message.encode('utf-8'), (UDP_IP, UDP_PORT))

print(f"Sent message to {UDP_IP}:{UDP_PORT}: {message}")
