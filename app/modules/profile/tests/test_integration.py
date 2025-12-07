"""
Integration tests for profile module.
"""

import pytest

from app import db
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile
from app.modules.profile.services import UserProfileService


@pytest.mark.integration
def test_profile_service_initialization(test_client):
    """Test UserProfileService can be initialized."""
    with test_client.application.app_context():
        service = UserProfileService()
        assert service is not None


@pytest.mark.integration
def test_create_user_profile(test_client):
    """Test creating a user profile."""
    with test_client.application.app_context():
        # Create a user first
        user = User(email="profiletest@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        # Create profile
        profile = UserProfile(user_id=user.id, name="Test", surname="User")
        db.session.add(profile)
        db.session.commit()

        assert profile.id is not None
        assert profile.name == "Test"
        assert profile.surname == "User"

        # Cleanup
        db.session.delete(profile)
        db.session.delete(user)
        db.session.commit()


@pytest.mark.integration
def test_get_user_profile(test_client):
    """Test getting a user profile."""
    with test_client.application.app_context():
        service = UserProfileService()

        # Create test user and profile
        user = User(email="gettest@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        profile = UserProfile(user_id=user.id, name="Get", surname="Test")
        db.session.add(profile)
        db.session.commit()

        # Test getting profile
        retrieved = service.get_by_id(profile.id)
        assert retrieved is not None
        assert retrieved.user_id == user.id
        assert retrieved.name == "Get"

        # Cleanup
        db.session.delete(profile)
        db.session.delete(user)
        db.session.commit()


@pytest.mark.integration
def test_update_user_profile(test_client):
    """Test updating a user profile."""
    with test_client.application.app_context():
        service = UserProfileService()

        # Create test user and profile
        user = User(email="updatetest@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        profile = UserProfile(user_id=user.id, name="Original", surname="Name")
        db.session.add(profile)
        db.session.commit()

        # Test update
        updated = service.update(profile.id, name="Updated Name")
        assert updated.name == "Updated Name"
        assert updated.surname == "Name"

        # Cleanup
        db.session.delete(profile)
        db.session.delete(user)
        db.session.commit()


@pytest.mark.integration
def test_profile_edit_page_requires_login(test_client):
    """Test that profile edit page requires authentication."""
    response = test_client.get("/profile/edit", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data


@pytest.mark.integration
def test_profile_edit_page_loads_when_logged_in(test_client, integration_test_data):
    """Test profile edit page loads for logged-in users."""
    # Login first
    test_client.post(
        "/login", data={"email": "user1@example.com", "password": "test1234"}, follow_redirects=True
    )

    # Access profile edit page
    response = test_client.get("/profile/edit")
    assert response.status_code == 200
    assert b"Edit profile" in response.data or b"Profile" in response.data

    # Logout
    test_client.get("/logout", follow_redirects=True)


@pytest.mark.integration
def test_profile_summary_page_requires_login(test_client):
    """Test that profile summary page requires authentication."""
    response = test_client.get("/profile/summary", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data


@pytest.mark.integration
def test_profile_summary_page_loads_when_logged_in(test_client, integration_test_data):
    """Test profile summary page loads for logged-in users."""
    # Login first
    test_client.post(
        "/login", data={"email": "user1@example.com", "password": "test1234"}, follow_redirects=True
    )

    # Access profile summary page
    response = test_client.get("/profile/summary")
    assert response.status_code == 200

    # Logout
    test_client.get("/logout", follow_redirects=True)


@pytest.mark.integration
def test_profile_summary_pagination(test_client, integration_test_data):
    """Test pagination on profile summary page."""
    # Login first
    test_client.post(
        "/login", data={"email": "user1@example.com", "password": "test1234"}, follow_redirects=True
    )

    # Access profile summary with pagination
    response = test_client.get("/profile/summary?page=1")
    assert response.status_code == 200

    # Logout
    test_client.get("/logout", follow_redirects=True)


@pytest.mark.integration
def test_profile_service_delete(test_client):
    """Test deleting a profile through service."""
    with test_client.application.app_context():
        service = UserProfileService()

        # Create test user and profile
        user = User(email="deletetest@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        profile = UserProfile(user_id=user.id, name="Delete", surname="Test")
        db.session.add(profile)
        db.session.commit()

        profile_id = profile.id

        # Delete through service
        service.delete(profile_id)

        # Verify deletion
        deleted = service.get_by_id(profile_id)
        assert deleted is None

        # Cleanup user
        db.session.delete(user)
        db.session.commit()


@pytest.mark.integration
def test_profile_model_attributes(test_client):
    """Test UserProfile model has expected attributes."""
    with test_client.application.app_context():
        user = User(email="attrtest@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        profile = UserProfile(user_id=user.id, name="Attr", surname="Test")
        db.session.add(profile)
        db.session.commit()

        assert hasattr(profile, 'id')
        assert hasattr(profile, 'user_id')
        assert hasattr(profile, 'name')
        assert hasattr(profile, 'surname')

        # Cleanup
        db.session.delete(profile)
        db.session.delete(user)
        db.session.commit()


@pytest.mark.integration
def test_profile_service_count(test_client):
    """Test counting profiles through service."""
    with test_client.application.app_context():
        service = UserProfileService()

        initial_count = service.count()

        # Create test user and profile
        user = User(email="counttest@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        profile = service.create(user_id=user.id, name="Count", surname="Test")

        assert service.count() == initial_count + 1

        # Cleanup
        service.delete(profile.id)
        db.session.delete(user)
        db.session.commit()

        assert service.count() == initial_count


@pytest.mark.integration
def test_profile_user_relationship(test_client):
    """Test relationship between profile and user."""
    with test_client.application.app_context():
        user = User(email="reltest@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        profile = UserProfile(user_id=user.id, name="Rel", surname="Test")
        db.session.add(profile)
        db.session.commit()

        # Test relationship
        assert profile.user is not None
        assert profile.user.email == "reltest@example.com"

        # Cleanup
        db.session.delete(profile)
        db.session.delete(user)
        db.session.commit()
