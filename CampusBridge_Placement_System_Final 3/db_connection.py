import os
import threading
import mysql.connector

HOST = os.environ.get("MYSQL_HOST", "localhost")
USER = os.environ.get("MYSQL_USER", "root")
DATABASE = os.environ.get("MYSQL_DATABASE", "placement_db")

# Support configured password, local password ('nikhil'), and previous fallback
candidate_passwords = [
    os.environ.get("MYSQL_PASSWORD"),
    "nikhil",
    "27^Someswar_wirE",
    "babbu@123",
    "",
]

_db_lock = threading.Lock()
server = None
cursor = None


def connect_database():
    global server, cursor
    for pwd in candidate_passwords:
        if pwd is None:
            continue
        try:
            conn = mysql.connector.connect(host=HOST, user=USER, password=pwd)
            conn.autocommit = True
            cur = conn.cursor(dictionary=True, buffered=True)
            cur.execute("CREATE DATABASE IF NOT EXISTS " + DATABASE)
            cur.execute("USE " + DATABASE)
            server = conn
            cursor = cur
            return server, cursor
        except mysql.connector.Error:
            continue
    raise RuntimeError("Failed to connect to MySQL server. Please verify credentials.")


connect_database()


def ensure_connection():
    global server, cursor
    if server is None or not server.is_connected():
        return connect_database()
    try:
        server.ping(reconnect=True, attempts=1, delay=0)
    except Exception:
        return connect_database()
    return server, cursor


def run(sql, values=()):
    """Use for INSERT, UPDATE, DELETE."""
    global server, cursor
    with _db_lock:
        try:
            ensure_connection()
            cursor.execute(sql, values)
            return True
        except mysql.connector.Error as e:
            print("Error:", e)
            return False


def show(sql, values=()):
    """Use for SELECT. Returns all rows as dictionaries."""
    global server, cursor
    with _db_lock:
        try:
            ensure_connection()
            cursor.execute(sql, values)
            rows = cursor.fetchall()
            return rows
        except mysql.connector.Error as e:
            print("Error:", e)
            return []
