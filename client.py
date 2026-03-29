import socket
import sys
import time

class Client:
    def __init__(self, server_ip='127.0.0.1', server_port=5555):
        self.server_ip = server_ip
        self.server_port = server_port
    
    def start_client(self):
        while True:
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #tcp
                print(f"[*] Attempting to connect to {self.server_ip}:{self.server_port}...")
                client.connect((self.server_ip, self.server_port))
                print("[+] Connected to C2 Server")

                while True:
                    command = client.recv(1024).decode()
                    
                    if not command:
                        break # connection lost

                    if command == "echo":
                        print("[*] Received 'echo' command")
                        client.send("Hello World".encode())
                    
                    elif command == "kill":
                        print("[!] Received 'kill' command. Shutting down...")
                        client.close()
                        sys.exit(0)
                    
            except (ConnectionRefusedError, ConnectionResetError):
                print("[-] Server unavailable, retrying in 5 seconds...")
                time.sleep(5)
            except Exception as e:
                print(f"[-] Error: {e}")
                break

if __name__ == "__main__":
    start_client()