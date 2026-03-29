import socket
import threading
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import dbManager

class C2Server:
    """
    encryption- asymmetric (RSA) for key exchange, symmetric (AES) for commands/data
    """
    def __init__(self, host='0.0.0.0', port=5555):
        db_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'dbname': os.getenv('DB_NAME', 'c2_db'),
            'user': os.getenv('DB_USER', 'admin'),
            'password': os.getenv('DB_PASS', 'password123')
        }
        self.db = dbManager.DatabaseManager(db_params)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #tcp
        self.server_socket.bind((host, port))
        self.server_socket.listen(5) # up to 5 clients
        self.clients = {}  # {id: (socket, address, key)}
        self.client_id_counter = 1
        self.db.log_event("INFO", "ServerInit", f"Server started on {host}:{port}")

    def init_handshake(self, client_socket):
        server_private = ec.generate_private_key(ec.SECP256R1())
        server_public_bytes = server_private.public_key().public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint)

        client_public_bytes = client_socket.recv(1024) # get client's public key
        client_socket.send(server_public_bytes)
        peer_public_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), client_public_bytes)
        shared_secret = server_private.exchange(ec.ECDH(), peer_public_key)

        final_key = HKDF(hashes.SHA256(), 32, None, b'c2 handshake').derive(shared_secret)
        return final_key
    
    def encrypt_data(self, data_str,key):
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, data_str.encode(), None)
        return nonce + ciphertext

    def decrypt_data(self, raw_data, key):
        aesgcm = AESGCM(key)
        nonce = raw_data[:12]
        ciphertext = raw_data[12:]
        return aesgcm.decrypt(nonce, ciphertext, None).decode()

    def listen_for_clients(self): #seperate thread for new clients
        print(f"[*] Server started on {self.server_socket.getsockname()}")
        while True:
            client_socket, addr = self.server_socket.accept()
            self.db.log_event("INFO", "Network", f"Connection attempt", addr)
            try:
                cid = self.client_id_counter
                client_key = self.init_handshake(client_socket) 
                self.clients[cid] = (client_socket, addr, client_key)
                print(f"\n[+] New Connection: {addr} (Assigned ID: {cid})")
                self.client_id_counter += 1
                self.db.log_event("INFO", "Handshake", "Success", addr)
            except Exception as e:
                print(f"[-] Error handling client {addr}: {e}")
                self.db.log_event("ERROR", "Handshake", f"Failed for {e}", addr)
                client_socket.close()

    def send_command(self, client_id, cmd):
        if client_id not in self.clients:
            print("[-] Invalid Client ID")
            return
        
        client_socket, _ , client_key = self.clients[client_id]
        try:
            data_to_send = self.encrypt_data(cmd, client_key)
            client_socket.send(data_to_send)
            if cmd == "kill":
                print(f"[*] Sent kill command to Client {client_id}")
                del self.clients[client_id]
            else:
                response = self.decrypt_data(client_socket.recv(1024), client_key)
                print(f"[*] Response from Client {client_id}: {response}")
            self.db.log_command(client_id, cmd, response)
        except Exception as e:
            print(f"[-] Error communicating with client {client_id}: {e}")
            self.db.log_event("ERROR", "Communication", f"Failed for {e}", self.clients[client_id][1])
            del self.clients[client_id]

    def run_cli(self):
        # assign listening thread
        threading.Thread(target=self.listen_for_clients, daemon=True).start() 

        while True:
            cmd_input = input("\nC2-Admin> ").strip().lower().split()
            if not cmd_input: continue
            
            action = cmd_input[0]

            if action == "list":
                print("\n--- Connected Clients ---")
                for cid, (sock, addr, _) in self.clients.items():
                    print(f"ID: {cid} | Address: {addr}")
            
            elif action == "echo" and len(cmd_input) > 1:
                self.send_command(int(cmd_input[1]), "echo")

            elif action == "kill" and len(cmd_input) > 1:
                self.send_command(int(cmd_input[1]), "kill")

            elif action == "exit":
                break
            else:
                print("Commands: list, echo <id>, kill <id>, exit")

if __name__ == "__main__":
    # main thred runs CLI, while listen thread gets new clients
    server = C2Server()
    server.run_cli()