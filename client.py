import socket
import sys
import time
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

class Client:
    def __init__(self, server_ip='127.0.0.1', server_port=5555):
        self.key = None # will be set after handshake
        self.server_ip = server_ip
        self.server_port = server_port
    
    def init_handshake(self, client_socket): #same as server but reversed
            private_key = ec.generate_private_key(ec.SECP256R1())
            public_bytes = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint
            )

            client_socket.send(public_bytes)
            server_public_bytes = client_socket.recv(1024)
            peer_public_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), server_public_bytes)
            shared_secret = private_key.exchange(ec.ECDH(), peer_public_key)

            final_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'c2 handshake',
            ).derive(shared_secret)
            
            return final_key


    # AES-GCM encryption/decryption- symmetric
    def encrypt_data(self, data_str, key):
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        return nonce + aesgcm.encrypt(nonce, data_str.encode(), None)

    def decrypt_data(self, raw_data, key):
        aesgcm = AESGCM(key)
        nonce = raw_data[:12]
        ciphertext = raw_data[12:]
        return aesgcm.decrypt(nonce, ciphertext, None).decode()
    
    def start_client(self):
        while True:
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #tcp
                print(f"[*] Attempting to connect to {self.server_ip}:{self.server_port}...")
                client.connect((self.server_ip, self.server_port))
                print("[+] Connected")
                self.key = self.init_handshake(client)
                print("[*] Handshake complete, secure channel established")

                while True:
                    enc_command = client.recv(1024)
                    command = self.decrypt_data(enc_command, self.key)
                    
                    if not command:
                        break # connection lost

                    if command == "echo":
                        print("[*] Received 'echo' command")
                        client.send(self.encrypt_data("!!Encrypted Hello World!!", self.key))
                    
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