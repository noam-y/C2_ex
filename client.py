import socket
import sys
import time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class Client:
    def __init__(self, server_ip='127.0.0.1', server_port=5555):
        self.key = b'this_is_a_32_byte_secret_keyyyyy' #TODO temp
        self.aesgcm = AESGCM(self.key)
        self.server_ip = server_ip
        self.server_port = server_port
    
    # AES-GCM encryption/decryption- symmetric
    def encrypt_data(self, data_str):
        nonce = os.urandom(12)
        return nonce + self.aesgcm.encrypt(nonce, data_str.encode(), None)

    def decrypt_data(self, raw_data):
        nonce = raw_data[:12]
        ciphertext = raw_data[12:]
        return self.aesgcm.decrypt(nonce, ciphertext, None).decode()
    
    def start_client(self):
        while True:
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #tcp
                print(f"[*] Attempting to connect to {self.server_ip}:{self.server_port}...")
                client.connect((self.server_ip, self.server_port))
                print("[+] Connected")

                while True:
                    enc_command = client.recv(1024)
                    command = self.decrypt_data(enc_command)
                    
                    if not command:
                        break # connection lost

                    if command == "echo":
                        print("[*] Received 'echo' command")
                        client.send(self.encrypt_data("!!Encrypted Hello World!!"))
                    
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
    c = Client()
    c.start_client()