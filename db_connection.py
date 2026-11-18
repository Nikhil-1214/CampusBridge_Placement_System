import os
import sqlite3
import threading

DB_TYPE = os.environ.get("DB_TYPE", "sqlite").lower()
DB_PATH = os.environ.get("DATABASE_PATH", os.environ.get("SQLITE_DB", "placement.db"))

_db_lock = threading.Lock()
server = None
cursor = None


def _rewrite_sql(sql):
    sql = sql.replace("%s", "?")
    sql = sql.replace("INT AUTO_INCREMENT PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
    sql = sql.replace("YEAR", "INTEGER")
    sql = sql.replace("BOOLEAN", "INTEGER")
    sql = sql.replace("DECIMAL(3,2)", "REAL")
    sql = sql.replace("DECIMAL(10,2)", "REAL")
    sql = sql.replace("DECIMAL(5,2)", "REAL")
    sql = sql.replace("DATETIME", "TEXT")
    sql = sql.replace("TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "TEXT DEFAULT CURRENT_TIMESTAMP")
    sql = sql.replace("CURDATE()", "date('now')")
    sql = sql.replace("NOW()", "datetime('now')")
    sql = sql.replace("FIND_IN_SET(", "find_in_set(")
    return sql


class SQLiteCursor:
    def __init__(self, connection):
        self._cursor = connection.cursor()

    def execute(self, sql, values=()):
        return self._cursor.execute(_rewrite_sql(sql), values)

    def fetchall(self):
        rows = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description] if self._cursor.description else []
        return [dict(zip(columns, row)) for row in rows]

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        columns = [column[0] for column in self._cursor.description]
        return dict(zip(columns, row))


def connect_database():
    global server, cursor
    if DB_TYPE == "sqlite":
        os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.create_function(
            "find_in_set",
            2,
            lambda needle, haystack: (
                1 + haystack.split(",").index(str(needle))
                if haystack and str(needle) in haystack.split(",")
                else 0
            ),
        )
        server = conn
        cursor = SQLiteCursor(conn)
        return server, cursor
    raise RuntimeError("Unsupported DB_TYPE. Use DB_TYPE=sqlite.")


connect_database()


def ensure_connection():
    return server, cursor


def run(sql, values=()):
    global server, cursor
    with _db_lock:
        try:
            ensure_connection()
            cursor.execute(sql, values)
            server.commit()
            return True
        except sqlite3.Error as e:
            print("Error:", e)
            return False


def show(sql, values=()):
    global server, cursor
    with _db_lock:
        try:
            ensure_connection()
            cursor.execute(sql, values)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print("Error:", e)
            return []
