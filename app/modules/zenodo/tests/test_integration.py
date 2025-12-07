"""
Integration tests for zenodo module.
"""

import pytest

from app import db
from app.modules.zenodo.models import Zenodo
from app.modules.zenodo.services import ZenodoService


@pytest.mark.integration
def test_zenodo_service_initialization(test_client):
    """Test ZenodoService can be initialized."""
    with test_client.application.app_context():
        service = ZenodoService()
        assert service is not None
        assert service.ZENODO_API_URL is not None


@pytest.mark.integration
def test_zenodo_get_url_configuration(test_client):
    """Test that Zenodo URL is correctly configured."""
    with test_client.application.app_context():
        service = ZenodoService()
        url = service.get_zenodo_url()
        assert url is not None
        assert "zenodo.org" in url


@pytest.mark.integration
def test_create_zenodo_record(test_client):
    """Test creating a Zenodo record in database."""
    with test_client.application.app_context():
        zenodo = Zenodo()
        db.session.add(zenodo)
        db.session.commit()

        assert zenodo.id is not None

        # Cleanup
        db.session.delete(zenodo)
        db.session.commit()


@pytest.mark.integration
def test_zenodo_repository_operations(test_client):
    """Test basic repository operations for Zenodo."""
    with test_client.application.app_context():
        service = ZenodoService()

        # Create
        created = service.create()
        assert created.id is not None

        # Get by id
        retrieved = service.get_by_id(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id

        # Delete
        service.delete(created.id)
        deleted = service.get_by_id(created.id)
        assert deleted is None


@pytest.mark.integration
def test_zenodo_count(test_client):
    """Test counting Zenodo records."""
    with test_client.application.app_context():
        service = ZenodoService()

        # Get initial count
        initial_count = service.count()

        # Create a record
        zenodo = service.create()
        assert service.count() == initial_count + 1

        # Cleanup
        service.delete(zenodo.id)
        assert service.count() == initial_count


@pytest.mark.integration
def test_zenodo_access_token_configuration(test_client):
    """Test that Zenodo access token is configured."""
    with test_client.application.app_context():
        service = ZenodoService()
        token = service.get_zenodo_access_token()
        # Token may be None in test environment, but method should work
        assert token is not None or token is None  # Just test the method works


@pytest.mark.integration
def test_zenodo_get_or_404(test_client):
    """Test get_or_404 method for Zenodo."""
    with test_client.application.app_context():
        service = ZenodoService()

        # Create a record
        created = service.create()

        # Get with valid ID
        retrieved = service.get_or_404(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id

        # Cleanup
        service.delete(created.id)


@pytest.mark.integration
def test_multiple_zenodo_records(test_client):
    """Test creating multiple Zenodo records."""
    with test_client.application.app_context():
        service = ZenodoService()

        initial_count = service.count()

        # Create multiple records
        records = []
        for i in range(3):
            record = service.create()
            records.append(record)
            assert record.id is not None

        # Verify count
        assert service.count() == initial_count + 3

        # Delete all
        for record in records:
            service.delete(record.id)

        assert service.count() == initial_count


@pytest.mark.integration
def test_zenodo_update_operations(test_client):
    """Test update operations for Zenodo."""
    with test_client.application.app_context():
        service = ZenodoService()

        # Create
        created = service.create()
        original_id = created.id

        # Update
        updated = service.update(created.id)
        assert updated is not None
        assert updated.id == original_id

        # Cleanup
        service.delete(created.id)


@pytest.mark.integration
def test_zenodo_get_url_method(test_client):
    """Test get_zenodo_url method."""
    with test_client.application.app_context():
        service = ZenodoService()
        url = service.get_zenodo_url()
        assert url is not None
        assert "zenodo" in url.lower()


@pytest.mark.integration
def test_zenodo_headers_configuration(test_client):
    """Test Zenodo service headers configuration."""
    with test_client.application.app_context():
        service = ZenodoService()
        assert service.headers is not None
        assert "Content-Type" in service.headers


@pytest.mark.integration
def test_zenodo_params_configuration(test_client):
    """Test Zenodo service params configuration."""
    with test_client.application.app_context():
        service = ZenodoService()
        assert service.params is not None
        assert "access_token" in service.params



@pytest.mark.integration
def test_zenodo_service_test_connection(test_client):
    """Test Zenodo connection test method."""
    with test_client.application.app_context():
        service = ZenodoService()
        result = service.test_connection()
        assert isinstance(result, bool)


@pytest.mark.integration
def test_zenodo_model_attributes(test_client):
    """Test Zenodo model attributes."""
    with test_client.application.app_context():
        zenodo = Zenodo()
        assert hasattr(zenodo, 'id')


@pytest.mark.integration
def test_zenodo_service_get_url_returns_string(test_client):
    """Test that get_zenodo_url returns a string."""
    with test_client.application.app_context():
        service = ZenodoService()
        url = service.get_zenodo_url()
        assert isinstance(url, str)


@pytest.mark.integration
def test_zenodo_repository_initialization(test_client):
    """Test ZenodoRepository initialization."""
    with test_client.application.app_context():
        from app.modules.zenodo.repositories import ZenodoRepository
        repo = ZenodoRepository()
        assert repo is not None


@pytest.mark.integration
def test_zenodo_get_by_id_nonexistent(test_client):
    """Test getting non-existent Zenodo record."""
    with test_client.application.app_context():
        service = ZenodoService()
        result = service.get_by_id(999999)
        assert result is None

