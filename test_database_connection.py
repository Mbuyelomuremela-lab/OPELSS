import importlib
import os
import tempfile
import unittest
from pathlib import Path


class DatabaseInitializationTest(unittest.TestCase):
    def test_create_app_initializes_database_schema(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_app.db"
            os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

            import config
            importlib.reload(config)

            import app as app_package
            importlib.reload(app_package)

            app = app_package.create_app()

            with app.app_context():
                from app.extensions import db
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()

            self.assertIn("users", tables)
            self.assertIn("announcements", tables)

            with app.app_context():
                from app.extensions import db as db_instance
                db_instance.session.remove()
                db_instance.engine.dispose()

            if db_path.exists():
                db_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
