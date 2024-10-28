# storage/sqlite_handler.py
import sqlite3

class SQLiteHandler:
    def __init__(self, db_name="downloads.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        """Create a table to store download information."""
        query = """
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            filename TEXT,
            status TEXT
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def save_download(self, url, filename, status):
        """Insert a download record into the database."""
        query = "INSERT INTO downloads (url, filename, status) VALUES (?, ?, ?)"
        self.conn.execute(query, (url, filename, status))
        self.conn.commit()

    def update_status(self, filename, status):
        """Update the status of a download (e.g., Paused, In Progress, Completed)."""
        query = "UPDATE downloads SET status = ? WHERE filename = ?"
        self.conn.execute(query, (status, filename))
        self.conn.commit()

    def fetch_all_downloads(self):
        """Retrieve all download records."""
        query = "SELECT * FROM downloads"
        return self.conn.execute(query).fetchall()
