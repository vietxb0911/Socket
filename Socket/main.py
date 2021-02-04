import socket
import signal # Allow socket destruction on Ctrl+C
import sys
import time
import threading


class WebServer(object):

    def __init__(self, port=80):
        self.host = '127.0.0.1' # Default to any avialable network interface
        self.port = port
        self.content_dir = 'files' # Directory where webpage files are stored

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            print("Starting server on {host}:{port}".format(host=self.host, port=self.port))
            self.socket.bind((self.host, self.port))
            print("Server started on port {port}.".format(port=self.port))

        except Exception as e:
            print("Error: Could not bind to port {port}".format(port=self.port))
            self.shutdown()
            sys.exit(1)

        self._listen() # Start listening for connections

    def shutdown(self):
    
        try:
            print("Shutting down server")
            self.socket.shutdown(socket.SHUT_RDWR)

        except Exception as e:
            pass # Pass if socket is already closed

    def _generate_headers(self, response_code):
        
        header = ''
        if response_code == 200:
            header += 'HTTP/1.1 200 OK\n'
        elif response_code == 301:
            header += 'HTTP/1.1 301 Moved permanently\n'
        elif response_code == 404:
            header += 'HTTP/1.1 404 Not Found\n'

        time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        header += 'Date: {now}\n'.format(now=time_now)
        header += 'Server: Simple-Python-Server\n'
        header += 'Connection: close\n\n' # Signal that connection will be closed after completing the request
        return header

    def _listen(self):
        
        self.socket.listen(5)
        while True:
            (client, address) = self.socket.accept()
            client.settimeout(60)
            print("Recieved connection from {addr}".format(addr=address))
            threading.Thread(target=self._handle_client, args=(client, address)).start()

    def _handle_client(self, client, address):
        
        PACKET_SIZE = 10000
        while True:
            print("CLIENT",client)
            data = client.recv(PACKET_SIZE).decode() # Recieve data packet from client and decode

            if not data: break

            request_method = data.split(' ')[0]
            print("Method: {m}".format(m=request_method))
            print("Request Body: {b}".format(b=data))

            if request_method == "GET" or request_method == "HEAD":
                
                file_requested = data.split(' ')[1]

                file_requested =  file_requested.split('?')[0]

                if file_requested == "/":
                    file_requested = "/index.html"

                filepath_to_serve = self.content_dir + file_requested
                print("Serving web page [{fp}]".format(fp=filepath_to_serve))

                # Load and Serve files content
                try:
                    f = open(filepath_to_serve, 'rb')
                    if request_method == "GET": # Read only for GET
                        response_data = f.read()
                    f.close()

                    response_header = self._generate_headers(200)

                except Exception as e:
                    print("Serving 404 page.")
                    response_header = self._generate_headers(404)

                    if request_method == "GET": # Temporary 404 Response Page
                        file_requested = "/404.html"

                        filepath_to_serve = self.content_dir + file_requested
                        print("Serving web page [{fp}]".format(fp=filepath_to_serve))

                        f = open(filepath_to_serve, 'rb')
                        response_data = f.read()
                        f.close()

                        response_header = self._generate_headers(404)

                response = response_header.encode()
                if request_method == "GET":
                    response += response_data

                client.send(response)
                client.close()
                break

            if request_method == 'POST':
                i = data.find("username=")
                j = data.rfind("&")
                nameuser = data[(i + len("username=")):j]
                password = data[(j + len("&password=")):]

                if (nameuser == "admin" and password == "admin"):
                    file_requested = "/redirect.html"

                    filepath_to_serve = self.content_dir + file_requested
                    print("Serving web page [{fp}]".format(fp=filepath_to_serve))

                    f = open(filepath_to_serve, 'rb')
                    response_data = f.read()
                    f.close()

                    response_header = self._generate_headers(301)
                else:
                    print("Serving 404 page.")

                    file_requested = "/404.html"

                    filepath_to_serve = self.content_dir + file_requested
                    print("Serving web page [{fp}]".format(fp=filepath_to_serve))

                    f = open(filepath_to_serve, 'rb')
                    response_data = f.read()
                    f.close()

                    response_header = self._generate_headers(404)

                response = response_header.encode()
                if request_method == "POST":
                    response += response_data

                client.send(response)
                client.close()
                break

            else:
                print("Unknown HTTP request method: {method}".format(method=request_method))




### MAIN ###
def shutdownServer(sig, unused):
    
    server.shutdown()
    sys.exit(1)

signal.signal(signal.SIGINT, shutdownServer)
server = WebServer(80)
server.start()
print("Press Ctrl+C to shut down server.")