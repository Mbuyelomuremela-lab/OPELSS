import importlib
import os
import tempfile
import unittest
from datetime import date, time
from pathlib import Path


class ReportsFiltersTest(unittest.TestCase):
    def test_reports_page_renders_preview_and_respects_date_and_multi_filters(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "reports_app.db"
            os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

            import config
            importlib.reload(config)

            import app as app_package
            importlib.reload(app_package)

            app = app_package.create_app()

            with app.app_context():
                from app.extensions import db
                from app.models.lab import Lab
                from app.models.province import Province
                from app.models.user import User
                from app.models.attendance import AttendanceLog

                province_1 = Province(name="Eastern Cape")
                province_2 = Province(name="KwaZulu-Natal")
                db.session.add_all([province_1, province_2])
                db.session.commit()

                lab_1 = Lab(name="Lab A", province_id=province_1.id, latitude=0.0, longitude=0.0, radius_meters=1000)
                lab_2 = Lab(name="Lab B", province_id=province_2.id, latitude=0.0, longitude=0.0, radius_meters=1000)
                db.session.add_all([lab_1, lab_2])
                db.session.commit()

                user = User(
                    full_name="HQ Admin",
                    email="hqadmin@opelss.com",
                    role="Manager",
                    active=True,
                    assigned_lab_id=lab_1.id,
                )
                user.set_password("Password123")
                db.session.add(user)
                db.session.commit()

                db.session.add_all([
                    AttendanceLog(
                        user_id=user.id,
                        lab_id=lab_1.id,
                        date=date(2026, 1, 10),
                        clock_in_time=time(8, 0),
                        clock_out_time=time(16, 0),
                    ),
                    AttendanceLog(
                        user_id=user.id,
                        lab_id=lab_2.id,
                        date=date(2026, 1, 20),
                        clock_in_time=time(9, 0),
                        clock_out_time=time(17, 0),
                    ),
                ])
                db.session.commit()
                user_id = user.id
                filtered_province_id = province_1.id
                filtered_lab_id = lab_1.id

            with app.test_client() as client:
                with client.session_transaction() as session:
                    session["_user_id"] = str(user_id)
                    session["_fresh"] = True

                response = client.get(
                    "/reports/?report_type=attendance"
                    f"&province_id={filtered_province_id}"
                    f"&lab_id={filtered_lab_id}"
                    "&start_date=2026-01-01"
                    "&end_date=2026-01-31"
                )

                self.assertEqual(response.status_code, 200)
                self.assertIn(b"Report Export Center", response.data)
                self.assertIn(b"2026-01-10", response.data)
                self.assertNotIn(b"2026-01-20", response.data)

                export_response = client.get(
                    "/reports/export/attendance"
                    f"?province_id={filtered_province_id}&lab_id={filtered_lab_id}&start_date=2026-01-01&end_date=2026-01-31"
                )
                self.assertEqual(export_response.status_code, 200)
                self.assertEqual(export_response.mimetype, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            with app.app_context():
                from app.extensions import db
                db.session.remove()
                db.engine.dispose()

            if db_path.exists():
                db_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
