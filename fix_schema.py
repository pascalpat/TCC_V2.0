#!/usr/bin/env python3
from app import create_app, db
from sqlalchemy import text

def main():
    app = create_app()
    with app.app_context():
        # 1) DAILY_NOTES: add columns if missing
        for col_sql in [
            "ALTER TABLE daily_notes ADD COLUMN content TEXT",
            "ALTER TABLE daily_notes ADD COLUMN work_order_id INTEGER"
        ]:
            try:
                db.session.execute(text(col_sql))
            except Exception:
                pass

        # back-fill content
        db.session.execute(text(
            "UPDATE daily_notes SET content = note "
            "WHERE content IS NULL"
        ))

        # 2) DAILY_PICTURES: add uploaded_at with default if missing
        try:
            db.session.execute(text(
                "ALTER TABLE daily_pictures "
                "ADD COLUMN uploaded_at DATETIME NOT NULL "
                "DEFAULT CURRENT_TIMESTAMP"
            ))
        except Exception:
            pass

        # 3) ENTRIES_MATERIAL: add date_of_report with default if missing
        try:
            db.session.execute(text(
                "ALTER TABLE entries_material "
                "ADD COLUMN date_of_report DATE NOT NULL "
                "DEFAULT (DATE('now'))"
            ))
        except Exception:
            pass

        db.session.commit()
        print("✅ Schema columns added & back-filled.")

if __name__ == "__main__":
    main()

