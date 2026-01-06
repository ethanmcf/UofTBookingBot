from pathlib import Path
import sqlite3, os
from uoftbookingbot.constants import DB_PATH


class DBController:

    _DB_SCHEMA_PATH = str(Path(__file__).parent / "schema.sql")

    def __init__(self, db_path=DB_PATH, schema_path=_DB_SCHEMA_PATH):
        """Initializes the connection and ensures the database schema is applied."""
        try:
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self._initialize_db(schema_path)  # Setup db if first time using
        except Exception as e:
            raise Exception(f"Failed to initialize database: {e}")

    def _initialize_db(self, schema_path):
        """Reads the schema.sql file and creates the necessary table structure."""
        try:
            # Only run the schema if the tables don't exist yet
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='account'"
            )
            if not self.cursor.fetchone():
                if os.path.exists(schema_path):
                    with open(schema_path, "r") as f:
                        schema_sql = f.read()
                    self.cursor.executescript(schema_sql)
                    self.conn.commit()
                else:
                    raise Exception(f"Schema file not found at {schema_path}")
        except Exception as e:
            raise Exception(f"Error applying schema: {e}")

    def get_credentials(self):
        """Retrieves the stored utorid and password for the single system user."""
        try:
            self.cursor.execute("SELECT utorid, password FROM account WHERE id = 1")
            result = self.cursor.fetchone()
            return result if result else (None, None)
        except Exception as e:
            raise Exception(f"Error retrieving credentials: {e}")

    def save_credentials(self, utorid, password):
        """
        Updates credentials. If a field is empty, the existing
        value in the database is preserved.
        """
        utorid_val = utorid if utorid.strip() else None
        pass_val = password if password.strip() else None

        if utorid_val is None and pass_val is None:
            return

        query = """
            INSERT INTO account (id, utorid, password) 
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET 
                utorid = COALESCE(excluded.utorid, account.utorid),
                password = COALESCE(excluded.password, account.password);
        """
        try:
            self.cursor.execute(query, (utorid_val, pass_val))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error saving credentials: {e}")

    def delete_user_data(self):
        """Wipes all bypass codes and account credentials from the database tables."""
        try:
            self.cursor.execute("DELETE FROM bypass_codes;")
            self.cursor.execute("DELETE FROM account;")
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error wiping security data: {e}")

    def save_bypass_codes(self, bypass_codes):
        """Iterates through a list of bypass codes and inserts them into the database."""
        try:
            for code in bypass_codes:
                self.cursor.execute("INSERT INTO bypass_codes (code) VALUES (?)", (code,))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error saving bypass codes: {e}")

    def get_next_bypass_code(self):
        """Retrieves the bypass code with the lowest ID from the system."""
        self.cursor.execute("SELECT code FROM bypass_codes ORDER BY id ASC LIMIT 1")
        result = self.cursor.fetchone()
        return result[0] if result else None

    def consume_bypass_code(self):
        """Retrieves and permanently removes the bypass code with the lowest ID from the system."""
        try:
            self.cursor.execute("SELECT id, code FROM bypass_codes ORDER BY id ASC LIMIT 1")
            result = self.cursor.fetchone()

            if result:
                code_id, code = result
                self.cursor.execute("DELETE FROM bypass_codes WHERE id = ?", (code_id,))
                self.conn.commit()
                return code
            return None
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error consuming bypass code: {e}")

    def get_num_codes_left(self):
        """Returns the number of bypass codes left in the codes file."""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM bypass_codes")
            num_codes = self.cursor.fetchone()
            return num_codes[0] if num_codes else 0
        except Exception as e:
            raise Exception(f"Error retrieving number of bypass codes: {e}")

    def add_scheduled_activity(self, activity_id, time, status="pending"):
        """Creates a new scheduled activity record with a activity_id, timestamp, and status."""
        query = "INSERT INTO activities (activity_id, scheduled_time, status) VALUES (?, ?, ?)"
        try:
            self.cursor.execute(query, (activity_id, time, status))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error adding scheduled activity: {e}")

    def get_scheduled_activities(self):
        """Returns a list of all activities currently stored in the database."""
        try:
            self.cursor.execute("SELECT * FROM activities")
            return self.cursor.fetchall()
        except Exception as e:
            raise Exception(f"Error retrieving scheduled activities: {e}")

    def close(self):
        """Safely closes the connection to the SQLite database file."""
        try:
            self.conn.close()
        except Exception as e:
            raise Exception(f"Error closing database connection: {e}")
