"""
Locust load testing file for Materials Hub.

This file consolidates all load testing scenarios for the application.

Usage:
    # Run with web UI
    locust --host=http://localhost:5000

    # Run headless with specific users
    locust --host=http://localhost:5000 --users 10 --spawn-rate 2 --run-time 1m --headless

    # Run specific test class
    locust --host=http://localhost:5000 AuthUser

Access web UI at: http://localhost:8089
"""

from locust import HttpUser, TaskSet, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import fake, get_csrf_token

# ============================================================================
# Authentication Tests
# ============================================================================


class SignupBehavior(TaskSet):
    def on_start(self):
        # Logout first to ensure we can access signup page
        self.client.get("/logout")
        self.signup()

    @task
    def signup(self):
        # Ensure logged out before signup
        self.client.get("/logout")

        response = self.client.get("/signup")

        # Check if we can see the signup form
        if "Sign up" not in response.text and "Signup" not in response.text:
            print("Cannot access signup page, may be redirected")
            return

        csrf_token = get_csrf_token(response)

        response = self.client.post(
            "/signup", data={"email": fake.email(), "password": fake.password(), "csrf_token": csrf_token}
        )
        if response.status_code != 200:
            print(f"Signup failed: {response.status_code}")


class LoginBehavior(TaskSet):
    def on_start(self):
        # Always logout first to ensure clean state
        self.client.get("/logout")
        self.login()

    def ensure_logged_out(self):
        """Ensure user is logged out before attempting login"""
        self.client.get("/logout")

    @task
    def login(self):
        # First, ensure we're logged out
        self.ensure_logged_out()

        response = self.client.get("/login")

        # Check if we were redirected (already logged in somehow)
        if "Login" not in response.text:
            print("Already logged in, forcing logout...")
            self.ensure_logged_out()
            response = self.client.get("/login")

        csrf_token = get_csrf_token(response)

        response = self.client.post(
            "/login", data={"email": "user1@example.com", "password": "1234", "csrf_token": csrf_token}
        )
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")


# ============================================================================
# Dataset Tests
# ============================================================================


class DatasetBehavior(TaskSet):
    def on_start(self):
        # Login first since dataset upload requires authentication
        self.login()

    def login(self):
        """Login before accessing dataset upload"""
        # Ensure logged out first
        self.client.get("/logout")
        response = self.client.get("/login")

        # Check if we can see the login form
        if "Login" not in response.text:
            print("Cannot access login page, may be already logged in")
            return

        try:
            csrf_token = get_csrf_token(response)
            self.client.post(
                "/login", data={"email": "user1@example.com", "password": "1234", "csrf_token": csrf_token}
            )
        except ValueError:
            print("CSRF token not found, login may fail")

    @task
    def dataset(self):
        # Access dataset upload page (requires login)
        response = self.client.get("/dataset/upload")

        # If not logged in, try login again
        if response.status_code == 302 or "Login" in response.text:
            self.login()
            response = self.client.get("/dataset/upload")


# ============================================================================
# Feature Model Tests
# ============================================================================


class FeaturemodelBehavior(TaskSet):
    def on_start(self):
        self.index()

    @task
    def index(self):
        response = self.client.get("/featuremodel")

        if response.status_code != 200:
            print(f"Featuremodel index failed: {response.status_code}")


# ============================================================================
# Flamapy Tests
# ============================================================================


class FlamapyBehavior(TaskSet):
    def on_start(self):
        self.check_uvl()

    @task
    def check_uvl(self):
        # Test check_uvl endpoint with file_id = 1
        response = self.client.get("/flamapy/check_uvl/1")

        if response.status_code not in [200, 404]:
            print(f"Flamapy check_uvl failed: {response.status_code}")

    @task
    def valid_uvl(self):
        # Test valid endpoint with file_id = 1
        response = self.client.get("/flamapy/valid/1")

        if response.status_code not in [200, 404]:
            print(f"Flamapy valid failed: {response.status_code}")


# ============================================================================
# Hubfile Tests
# ============================================================================


class HubfileBehavior(TaskSet):
    def on_start(self):
        self.view_file()

    @task
    def view_file(self):
        # Test file view endpoint with file_id = 1
        response = self.client.get("/file/view/1")

        if response.status_code not in [200, 404]:
            print(f"Hubfile view failed: {response.status_code}")

    @task
    def download_file(self):
        # Test file download endpoint with file_id = 1
        response = self.client.get("/file/download/1")

        if response.status_code not in [200, 404]:
            print(f"Hubfile download failed: {response.status_code}")


# ============================================================================
# User Classes
# ============================================================================


class AuthUser(HttpUser):
    """Load testing for authentication endpoints (login/signup)"""

    tasks = [SignupBehavior, LoginBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()


class DatasetUser(HttpUser):
    """Load testing for dataset upload functionality"""

    tasks = [DatasetBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()


class FeaturemodelUser(HttpUser):
    """Load testing for feature model endpoints"""

    tasks = [FeaturemodelBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()


class FlamapyUser(HttpUser):
    """Load testing for Flamapy endpoints"""

    tasks = [FlamapyBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()


class HubfileUser(HttpUser):
    """Load testing for file view/download endpoints"""

    tasks = [HubfileBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
