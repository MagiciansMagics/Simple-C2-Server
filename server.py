import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs  # Add this import

# TCP Server for clients
class TCPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.connections = {}  # Dictionary to store client connections and their statuses
        self.added_clients = 0
        self.disconnected_clients = 0
        self.lock = threading.Lock()  # Lock to ensure thread-safe access to connections dictionary

    def handle_client(self, client_socket, client_address):
        # Handle incoming connections
        print(f"Accepted connection from {client_address}")
        self.lock.acquire()  # Acquire lock before accessing shared data
        self.connections[client_address] = client_socket  # Add client to connections dictionary
        self.added_clients += 1
        self.lock.release()  # Release lock after modifying shared data
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            # Process received data here
            print(f"Received data from {client_address}: {data.decode()}")
        self.lock.acquire()  # Acquire lock before accessing shared data
        self.connections.pop(client_address)  # Remove client from connections dictionary
        self.disconnected_clients += 1
        self.lock.release()  # Release lock after modifying shared data

    def send_data_to_clients(self, data):
        for address, connection in self.connections.items():
            try:
                connection.sendall(data.encode())
            except Exception as e:
                print(f"Error sending data to {address}: {e}")
                # Handle error gracefully, no need to remove client from connections dictionary

    def get_num_clients(self):
        return len(self.connections)

    def get_added_clients(self):
        return self.added_clients

    def get_disconnected_clients(self):
        return self.disconnected_clients

    def get_connected_clients_info(self):
        return [(address, "Connected" if address in self.connections else "Offline") for address in self.connections]

    def start(self):
        self.socket.listen(5)
        print(f"TCP Server listening on {self.host}:{self.port}")
        while True:
            client_socket, client_address = self.socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()

# HTTP Server for controller
class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Handle HTTP GET requests
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write('<html><body><h1>Controller Page</h1>'.encode())
            self.wfile.write('<form action="/send_data" method="post">'.encode())
            self.wfile.write('<input type="text" name="data"><br>'.encode())
            self.wfile.write('<input type="submit" value="Send Data">'.encode())
            self.wfile.write('</form></body></html>'.encode())
        elif self.path == '/stats':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            num_clients = tcp_server.get_num_clients()
            added_clients = tcp_server.get_added_clients()
            disconnected_clients = tcp_server.get_disconnected_clients()
            connected_clients_info = tcp_server.get_connected_clients_info()
            self.wfile.write(f"<html><body><h1>Controller Page</h1><p>Number of Connected Clients: {num_clients}</p><p>Added Clients: {added_clients}</p><p>Disconnected Clients: {disconnected_clients}</p>".encode())
            self.wfile.write(b"<div><h2>Connected Clients:</h2><ul>")
            for client_address, status in connected_clients_info:
                self.wfile.write(f"<li>{client_address} - {status}</li>".encode())
            self.wfile.write(b"</ul></div></body></html>")
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<html><body><h1>404 Not Found</h1></body></html>".encode())

    def do_POST(self):
        # Handle HTTP POST requests
        if self.path == '/send_data':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = post_data.split('=')[1]  # Extract data from the POST request
            if data:
                tcp_server.send_data_to_clients(data)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write('<html><body><h1>Controller Page</h1>'.encode())
            self.wfile.write('<p>Data sent successfully!</p>'.encode())
            self.wfile.write('<a href="/">Back to Home</a></body></html>'.encode())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<html><body><h1>404 Not Found</h1></body></html>".encode())

def start_http_server(host, port):
    http_server = HTTPServer((host, port), HTTPRequestHandler)
    print(f"HTTP Server listening on {host}:{port}")
    http_server.serve_forever()

if __name__ == "__main__":
    tcp_server = TCPServer("0.0.0.0", 12001)
    tcp_server_thread = threading.Thread(target=tcp_server.start)
    tcp_server_thread.start()

    http_server_thread = threading.Thread(target=start_http_server, args=("0.0.0.0", 12000))
    http_server_thread.start()
