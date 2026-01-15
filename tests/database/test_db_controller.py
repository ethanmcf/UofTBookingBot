import pytest
from uoftbookingbot.database.db_controller import DBController


@pytest.fixture
def db(tmp_path) -> DBController:
    """Creates a temporary test database and applies the actual project schema."""
    test_db = tmp_path / "test_db.db"

    return DBController(test_db)


class TestDatabase:
    """Unit tests for the database controller class"""

    def test_save_and_get_credentials(self, db):
        """Tests if credentials can be saved and then accurately retrieved."""
        db.save_credentials("test_user", "secure_pass")
        utorid, password = db.get_credentials()
        assert utorid == "test_user"
        assert password == "secure_pass"

    def test_update_credentials(self, db):
        """Tests the upsert logic by updating an existing user's password."""
        db.save_credentials("user1", "old_pass")
        db.save_credentials("user2", "new_pass")
        utorid, password = db.get_credentials()
        assert utorid == "user2"
        assert password == "new_pass"

    def test_save_and_consume_bypass_code(self, db):
        """Tests that bypass codes are retrieved in FIFO order and then removed."""
        codes = ["code1", "code2"]
        db.save_bypass_codes(codes)

        first_code = db.consume_bypass_code()
        assert first_code == "code1"

        second_code = db.consume_bypass_code()
        assert second_code == "code2"

        # Verify it returns None when empty
        assert db.consume_bypass_code() is None

    def test_delete_user_data(self, db):
        """Tests that all sensitive information is wiped correctly."""
        db.save_credentials("admin", "1234")
        db.save_bypass_codes(["code1"])

        db.delete_user_data()

        utorid, password = db.get_credentials()
        assert utorid is None
        assert password is None
        assert db.consume_bypass_code() is None

    def test_get_num_codes_left(self, db):
        """Tests that the code counter accurately reflects the database state."""
        assert db.get_num_codes_left() == 0

        test_codes = ["11111111", "22222222", "33333333"]
        db.save_bypass_codes(test_codes)
        assert db.get_num_codes_left() == 3

        db.consume_bypass_code()
        assert db.get_num_codes_left() == 2

        db.delete_user_data()
        assert db.get_num_codes_left() == 0
