# database.py
import sqlite3
from typing import List, Dict, Any, Optional, Tuple

class DatabaseManager:
    """Manages all database operations for the Valorant account tracker."""

    def __init__(self, db_file: str):
        """Initializes the DatabaseManager with the path to the SQLite database file."""
        self.db_file = db_file
        self._create_connection()

    def _create_connection(self) -> sqlite3.Connection:
        """Creates and returns a database connection."""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row  # Allows accessing columns by name
        return conn

    def setup(self):
        """Initializes the database schema, creating tables and adding columns if they don't exist."""
        with self._create_connection() as conn:
            cursor = conn.cursor()
            # Create accounts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    username TEXT NOT NULL,
                    hashtag TEXT NOT NULL,
                    region TEXT NOT NULL,
                    rank TEXT,
                    rr INTEGER,
                    password TEXT,
                    account_username TEXT,
                    section TEXT DEFAULT 'Default',
                    PRIMARY KEY (username, hashtag, region)
                )
            ''')
            # Create sections table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sections (
                    name TEXT PRIMARY KEY NOT NULL
                )
            ''')
            # Add a default section if none exist
            cursor.execute("INSERT OR IGNORE INTO sections (name) VALUES (?)", ('Default',))
            conn.commit()
            print("Database setup complete.")

    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """Retrieves all accounts from the database, ordered by username."""
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts ORDER BY username")
            return [dict(row) for row in cursor.fetchall()]

    def get_sections(self) -> List[Dict[str, Any]]:
        """Retrieves all section names from the database."""
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sections ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]

    def save_account(self, data: Dict[str, Any]):
        """Saves or updates an account in the database."""
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO accounts 
                (username, hashtag, region, account_username, password, rank, rr, section) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data['username'], data['hashtag'], data['region'],
                    data['account_username'], data['password'],
                    data.get('rank'), data.get('rr'), data['section']
                )
            )
            conn.commit()

    def delete_account(self, username: str, hashtag: str, region: str):
        """Deletes an account from the database."""
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM accounts WHERE username = ? AND hashtag = ? AND region = ?",
                (username, hashtag, region)
            )
            conn.commit()

    def create_section(self, section_name: str):
        """Creates a new section."""
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO sections (name) VALUES (?)", (section_name,))
            conn.commit()

    def delete_section(self, section_name: str):
        """Deletes a section and moves its accounts to the 'Default' section."""
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE accounts SET section = 'Default' WHERE section = ?", (section_name,))
            cursor.execute("DELETE FROM sections WHERE name = ?", (section_name,))
            conn.commit()

    def update_account_rank(self, username: str, hashtag: str, region: str, rank: str, rr: int):
        """Updates the rank and RR for a specific account."""
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE accounts SET rank = ?, rr = ? WHERE username = ? AND hashtag = ? AND region = ?",
                (rank, rr, username, hashtag, region)
            )
            conn.commit()