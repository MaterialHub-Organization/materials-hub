#!/usr/bin/env python
"""
Script to start Flask app in testing mode for Selenium tests.
"""
import os

os.environ["FLASK_ENV"] = "testing"
os.environ["WORKING_DIR"] = ""
os.environ["WDM_LOCAL"] = "1"  # Disable webdriver-manager downloads

from app import create_app, db  # noqa: E402
from app.modules.auth.seeders import AuthSeeder  # noqa: E402

if __name__ == "__main__":
    app = create_app("testing")

    # Setup database and seed data for Selenium tests
    with app.app_context():
        print("Setting up test database...")
        db.drop_all()
        db.create_all()

        print("Seeding test data...")
        # Run auth seeder to create test users
        auth_seeder = AuthSeeder()
        auth_seeder.run()
        print("Test data seeded successfully")

    print("Starting Flask app for testing on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
