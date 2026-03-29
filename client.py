import socket
import sys
import time

def start_client(server_ip='127.0.0.1', server_port=5555): #default to localhost and port 5555
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #tcp
            print(f"[*] Attempting to connect to {server_ip}:{server_port}...")
            client.connect((server_ip, server_port))
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