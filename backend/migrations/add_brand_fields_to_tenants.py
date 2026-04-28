"""
Add brand_name and brand_logo fields to tenants table
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def migrate():
    app = create_app()
    with app.app_context():
        try:
            result = db.session.execute(db.text("PRAGMA table_info(tenants)"))
            columns = [row[1] for row in result]

            fields_added = []

            if 'brand_name' not in columns:
                db.session.execute(db.text(
                    "ALTER TABLE tenants ADD COLUMN brand_name VARCHAR(100)"
                ))
                fields_added.append('brand_name')

            if 'brand_logo' not in columns:
                db.session.execute(db.text(
                    "ALTER TABLE tenants ADD COLUMN brand_logo VARCHAR(500)"
                ))
                fields_added.append('brand_logo')

            if fields_added:
                db.session.commit()
                print(f"Success: Added fields {', '.join(fields_added)}")
            else:
                print("All fields already exist")

        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {str(e)}")
            raise

if __name__ == '__main__':
    migrate()
