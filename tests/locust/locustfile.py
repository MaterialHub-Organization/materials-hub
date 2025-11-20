"""
Locust load testing file for Materials Hub.

This file defines load testing scenarios to simulate multiple users
accessing the application concurrently to measure performance and identify bottlenecks.

Usage:
    # Run with web UI
    locust -f tests/locust/locustfile.py --host=http://localhost:5000

    # Run headless with specific users
    locust -f tests/locust/locustfile.py --host=http://localhost:5000 \
           --users 100 --spawn-rate 10 --run-time 1m --headless

    # Run with specific test class
    locust -f tests/locust/locustfile.py --host=http://localhost:5000 \
           WebsiteUser

Access web UI at: http://localhost:8089
"""

from locust import HttpUser, TaskSet, between, task


class PublicUserBehavior(TaskSet):
    """
    Simulates behavior of anonymous users browsing the public website.
    """

    @task(5)
    def view_homepage(self):
        """Visit the homepage (most common action)"""
        self.client.get("/")

    @task(3)
    def browse_datasets(self):
        """Browse datasets in explore page"""
        self.client.get("/explore")

    @task(2)
    def search_datasets(self):
        """Search for datasets with various queries"""
        queries = ["machine learning", "data science", "materials", "test"]
        for query in queries:
            self.client.get(f"/explore?query={query}")

    @task(1)
    def view_dataset_detail(self):
        """View a specific dataset detail page"""
        # Assuming dataset IDs start from 1
        dataset_id = 1
        self.client.get(f"/dataset/view/{dataset_id}")

    @task(1)
    def view_signup_page(self):
        """View the signup page"""
        self.client.get("/signup")

    @task(1)
    def view_login_page(self):
        """View the login page"""
        self.client.get("/login")


class AuthenticatedUserBehavior(TaskSet):
    """
    Simulates behavior of logged-in users performing authenticated actions.
    """

    def on_start(self):
        """Called when a simulated user starts - performs login"""
        self.login()

    def login(self):
        """Attempt to login with test credentials"""
        response = self.client.post(
            "/login",
            data={"email": "test@example.com", "password": "test1234"},
            allow_redirects=True,
        )
        if response.status_code == 200:
            print("Login successful")
        else:
            print(f"Login failed: {response.status_code}")

    @task(5)
    def view_homepage(self):
        """Visit homepage as authenticated user"""
        self.client.get("/")

    @task(4)
    def view_profile(self):
        """View user profile"""
        self.client.get("/profile/summary")

    @task(3)
    def browse_datasets(self):
        """Browse datasets"""
        self.client.get("/explore")

    @task(2)
    def search_datasets(self):
        """Search for datasets"""
        queries = ["test", "example", "data"]
        for query in queries:
            self.client.get(f"/explore?query={query}")

    @task(1)
    def view_own_datasets(self):
        """View own uploaded datasets (if route exists)"""
        self.client.get("/dataset/list")

    def on_stop(self):
        """Called when a simulated user stops - performs logout"""
        self.client.get("/logout")


class DatasetUploadBehavior(TaskSet):
    """
    Simulates users uploading and managing datasets (heavy operations).
    """

    def on_start(self):
        """Login before starting"""
        self.client.post(
            "/login",
            data={"email": "test@example.com", "password": "test1234"},
        )

    @task(3)
    def view_upload_form(self):
        """View the dataset upload form"""
        self.client.get("/dataset/upload")

    @task(2)
    def view_my_datasets(self):
        """View user's own datasets"""
        self.client.get("/dataset/list")

    @task(1)
    def view_dataset_detail(self):
        """View dataset details"""
        dataset_id = 1
        self.client.get(f"/dataset/view/{dataset_id}")


class APIUserBehavior(TaskSet):
    """
    Simulates API consumers making requests to API endpoints.
    """

    @task(5)
    def api_list_datasets(self):
        """List datasets via API"""
        self.client.get("/api/v1/datasets/", name="/api/v1/datasets/")

    @task(3)
    def api_get_dataset(self):
        """Get specific dataset via API"""
        dataset_id = 1
        self.client.get(f"/api/v1/datasets/{dataset_id}", name="/api/v1/datasets/[id]")

    @task(2)
    def api_search_datasets(self):
        """Search datasets via API"""
        self.client.get("/api/v1/datasets/?query=test", name="/api/v1/datasets/?query=[q]")


class PublicUser(HttpUser):
    """
    Represents an anonymous public user browsing the website.

    Weight: 50 (most common user type)
    Wait time: 1-5 seconds between tasks (realistic browsing)
    """

    tasks = [PublicUserBehavior]
    weight = 50
    wait_time = between(1, 5)


class AuthenticatedUser(HttpUser):
    """
    Represents a logged-in user using the application.

    Weight: 30 (common user type)
    Wait time: 2-6 seconds between tasks
    """

    tasks = [AuthenticatedUserBehavior]
    weight = 30
    wait_time = between(2, 6)


class DatasetUploader(HttpUser):
    """
    Represents users uploading and managing datasets.

    Weight: 15 (less common, heavier operations)
    Wait time: 3-8 seconds between tasks
    """

    tasks = [DatasetUploadBehavior]
    weight = 15
    wait_time = between(3, 8)


class APIUser(HttpUser):
    """
    Represents API consumers making programmatic requests.

    Weight: 5 (least common)
    Wait time: 0.5-2 seconds (APIs are used by programs, faster)
    """

    tasks = [APIUserBehavior]
    weight = 5
    wait_time = between(0.5, 2)


# Advanced Locust features


class StressTestUser(HttpUser):
    """
    Stress test user - makes rapid requests to stress the system.
    Use sparingly to test system limits.

    Usage:
        locust -f tests/locust/locustfile.py --host=http://localhost:5000 StressTestUser
    """

    wait_time = between(0.1, 0.5)  # Very short wait times

    @task(10)
    def rapid_homepage_requests(self):
        """Make rapid homepage requests"""
        self.client.get("/")

    @task(5)
    def rapid_explore_requests(self):
        """Make rapid explore page requests"""
        self.client.get("/explore")

    @task(3)
    def rapid_search_requests(self):
        """Make rapid search requests"""
        self.client.get("/explore?query=test")
