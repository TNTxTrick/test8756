"""Local server for testing."""

import socket
import sys


class Server:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

        # The server will respond with a 200 HTTP status code and a message
        self.response = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nIt's all working!!"

        # Establishing IPv4 and TCP protocols for the server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Allowing the server to reuse the same address when needed
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def __enter__(self):
        """Set up the server and bind to the specified host and port."""
        try:
            self.sock.bind((self.host, self.port))
        except Exception as e:
            print(f"Failed to bind server: {e}")
            sys.exit(1)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the server socket."""
        self.sock.close()

    def start(self):
        """Start listening for incoming connections and handle them."""
        self.sock.listen()
        print(f"Server running on http://{self.host}:{self.port}/")

        while True:
            try:
                # Accept a client connection
                conn, addr = self.sock.accept()
                print(f"Connected by {addr}")

                # Decode client's request
                request_data = conn.recv(1024).decode()
                print(f"Request:\n{request_data}")

                # Send response to client
                conn.sendall(self.response)
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                # Always close the connection
                conn.close()


def main():
    """Main function to start the server."""
    # Default HTTP server settings
    HOST, PORT = "127.0.0.1", 8080
    with Server(HOST, PORT) as server:
        server.start()


if __name__ == "__main__":
    main()
