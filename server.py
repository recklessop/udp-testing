import socket
import threading
import http.server
import socketserver
from datetime import datetime
import signal
import sys

# Define the IP address and port for the UDP server
UDP_IP = "0.0.0.0"  # Bind to all available interfaces
UDP_PORT = 12345    # Port to listen on for UDP packets
HTTP_PORT = 12321   # Port to listen for HTTP interface packets

# for web interface go to http://serverip/clients

# List to store unique client info (IP, Port, Date, Data)
client_info = []

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the address and port
sock.bind((UDP_IP, UDP_PORT))

# Flag to indicate when the server should stop
stop_server = False

# Function to receive UDP packets and track client info
def udp_listener():
    global stop_server
    print(f"UDP server is listening on port {UDP_PORT}...")
    while not stop_server:
        sock.settimeout(1.0)  # Timeout so it can periodically check the stop_server flag
        try:
            data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
            client_ip = addr[0]
            client_port = addr[1]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = data.decode('utf-8')

            # Check if this client is already in the list
            existing_client = False
            for client in client_info:
                if client[0] == client_ip and client[1] == client_port:
                    existing_client = True
                    break

            # Add new client info to the list if it's a new client or new port
            if not existing_client:
                print(f"Received packet from new client: IP {client_ip}, Port {client_port} at {timestamp} with data: {message}")
                client_info.append((client_ip, client_port, timestamp, message))
            else:
                print(f"Received packet from existing client: IP {client_ip}, Port {client_port} with data: {message}")
        except socket.timeout:
            continue

# HTTP Request Handler to display client info and handle clearing the list
class ClientIPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/clients":
            # Build HTML response with client info
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            response = "<html><head><title>Client Info</title>"
            response += "<meta http-equiv='refresh' content='5'>"  # Auto-refresh every 5 seconds
            response += "</head><body>"
            response += "<h1>Clients that have sent UDP packets:</h1>"
            
            # Add a form with a "Clear" button to reset the list
            response += "<form method='POST' action='/clear'><input type='submit' value='Clear List'></form>"

            # Display the list of clients in a table (including data)
            response += "<table border='1'><tr><th>IP</th><th>Port</th><th>Date</th><th>Data</th></tr>"
            for client in client_info:
                response += f"<tr><td>{client[0]}</td><td>{client[1]}</td><td>{client[2]}</td><td>{client[3]}</td></tr>"
            response += "</table>"

            response += "</body></html>"
            self.wfile.write(response.encode())
        else:
            super().do_GET()

    # Handle the POST request for clearing the list
    def do_POST(self):
        if self.path == "/clear":
            # Clear the client info list
            global client_info
            client_info = []

            # Redirect back to the clients page
            self.send_response(303)
            self.send_header("Location", "/clients")
            self.end_headers()

# Function to start the web server
def start_web_server():
    with socketserver.TCPServer(("", HTTP_PORT), ClientIPRequestHandler) as httpd:
        print(f"Web server running on port {PORT}...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down web server...")
            httpd.shutdown()

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    global stop_server
    print("\nCtrl+C detected, shutting down...")
    stop_server = True  # Set the flag to stop the UDP listener
    sock.close()  # Close the UDP socket
    sys.exit(0)   # Exit the program

# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Start the UDP listener in a separate thread
udp_thread = threading.Thread(target=udp_listener)
udp_thread.start()

# Start the web server in the main thread
start_web_server()
