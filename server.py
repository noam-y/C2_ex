import socket
import threading
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class C2Server:
    """
    encryption- asymmetric (RSA) for key exchange, symmetric (AES) for commands/data
    """
    def __init__(self, host='0.0.0.0', port=5555):
        self.key = b'this_is_a_32_byte_secret_keyyyyy' #TODO temp
        self.aesgcm = AESGCM(self.key)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #tcp
        self.server_socket.bind((host, port))
        self.server_socket.listen(5) # up to 5 clients
        self.clients = {}  # {id: (socket, address)}
        self.client_id_counter = 1

    def encrypt_data(self, data_str):
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, data_str.encode(), None)
        return nonce + ciphertext

    def decrypt_data(self, raw_data):
        nonce = raw_data[:12]
        ciphertext = raw_data[12:]
        return self.aesgcm.decrypt(nonce, ciphertext, None).decode()

    def listen_for_clients(self): #seperate thread for new clients
        print(f"[*] Server started on {self.server_socket.getsockname()}")
        while True:
            client_socket, addr = self.server_socket.accept()
            cid = self.client_id_counter
            self.clients[cid] = (client_socket, addr)
            print(f"\n[+] New Connection: {addr} (Assigned ID: {cid})")
            self.client_id_counter += 1

    def send_command(self, client_id, cmd):
        if client_id not in self.clients:
            print("[-] Invalid Client ID")
            return
        
        client_socket, _ = self.clients[client_id]
        try:
            data_to_send = self.encrypt_data(cmd)
            client_socket.send(data_to_send)
            if cmd == "kill":
                print(f"[*] Sent kill command to Client {client_id}")
                del self.clients[client_id]
            else:
                response = self.decrypt_data(client_socket.recv(1024)) 
                print(f"[*] Response from Client {client_id}: {response}")
        except Exception as e:
            print(f"[-] Error communicating with client {client_id}: {e}")
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
                for cid, (sock, addr) in self.clients.items():
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