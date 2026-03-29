import psycopg2
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_params):
        self.params = db_params
        self.conn = None
        self._connect()

    def _connect(self):
        try:
            self.conn = psycopg2.connect(**self.params)
        except Exception as e:
            print(f"[-] Critical: Could not connect to DB: {e}")

    def log_command(self, client_id, command, result, status="SUCCESS"):
        if not self.conn: return
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO command_history (client_id, command, result, status) VALUES (%s, %s, %s, %s)",
                    (client_id, command, result, status)
                )
            self.conn.commit()
        except Exception as e:
            print(f"[-] DB Error (Command): {e}")
            self.conn.rollback()

    def log_event(self, level, source, message, client_addr=None):
        if not self.conn: return
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO system_logs (level, source, message, client_addr) VALUES (%s, %s, %s, %s)",
                    (level, source, message, str(client_addr))
                )
            self.conn.commit()
        except Exception as e:
            print(f"[-] DB Error (Log): {e}")
            self.conn.rollback()