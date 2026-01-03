import sqlite3, os


class DBController:
    def __init__(self, db_path="database/database.db", schema_path="database/schema.sql"):
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
        """Inserts a new user record or updates existing credentials if the user already exists."""
        query = """
            INSERT INTO account (id, utorid, password) 
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET 
                utorid = excluded.utorid,
                password = excluded.password;
            """
        try:
            self.cursor.execute(query, (utorid, password))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Error saving credentials: {e}")

    def delete_security_data(self):
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
