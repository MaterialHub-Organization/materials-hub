"""
Integration tests for fakenodo module.
"""

import pytest

from app import db
from app.modules.fakenodo.models import Deposition
from app.modules.fakenodo.services import FakenodoService


@pytest.mark.integration
def test_fakenodo_service_initialization(test_client):
    """Test FakenodoService can be initialized."""
    with test_client.application.app_context():
        service = FakenodoService()
        assert service is not None


@pytest.mark.integration
def test_create_deposition_record(test_client):
    """Test creating a Deposition record in database."""
    with test_client.application.app_context():
        deposition = Deposition(dep_metadata={"title": "Test"}, status="draft")
        db.session.add(deposition)
        db.session.commit()

        assert deposition.id is not None

        # Cleanup
        db.session.delete(deposition)
        db.session.commit()


@pytest.mark.integration
def test_deposition_repository_operations(test_client):
    """Test basic repository operations for Deposition."""
    with test_client.application.app_context():
        service = FakenodoService()

        # Create
        created = service.create(dep_metadata={"title": "Test Deposition"}, status="draft")
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
def test_deposition_update(test_client):
    """Test updating a Deposition record."""
    with test_client.application.app_context():
        service = FakenodoService()

        # Create
        created = service.create(dep_metadata={"title": "Original Title"}, status="draft")
        assert created.dep_metadata["title"] == "Original Title"

        # Update
        updated = service.update(created.id, dep_metadata={"title": "Updated Title"})
        assert updated.dep_metadata["title"] == "Updated Title"

        # Cleanup
        service.delete(created.id)


@pytest.mark.integration
def test_deposition_count(test_client):
    """Test counting depositions."""
    with test_client.application.app_context():
        service = FakenodoService()

        # Get initial count
        initial_count = service.count()

        # Create a deposition
        deposition = service.create(dep_metadata={"title": "Count Test"}, status="draft")
        assert service.count() == initial_count + 1

        # Cleanup
        service.delete(deposition.id)
        assert service.count() == initial_count


@pytest.mark.integration
def test_deposition_status_values(test_client):
    """Test creating depositions with different status values."""
    with test_client.application.app_context():
        service = FakenodoService()

        # Create with draft status
        draft = service.create(dep_metadata={"title": "Draft"}, status="draft")
        assert draft.status == "draft"

        # Create with published status
        published = service.create(dep_metadata={"title": "Published"}, status="published")
        assert published.status == "published"

        # Cleanup
        service.delete(draft.id)
        service.delete(published.id)


@pytest.mark.integration
def test_deposition_metadata_structure(test_client):
    """Test deposition metadata structure."""
    with test_client.application.app_context():
        service = FakenodoService()

        metadata = {"title": "Test Title", "description": "Test Description", "creators": [{"name": "John Doe"}]}

        deposition = service.create(dep_metadata=metadata, status="draft")
        assert deposition.dep_metadata["title"] == "Test Title"
        assert deposition.dep_metadata["description"] == "Test Description"
        assert len(deposition.dep_metadata["creators"]) == 1

        # Cleanup
        service.delete(deposition.id)


@pytest.mark.integration
def test_deposition_get_or_404(test_client):
    """Test get_or_404 method."""
    with test_client.application.app_context():
        service = FakenodoService()

        # Create a deposition
        created = service.create(dep_metadata={"title": "Test"}, status="draft")

        # Get with valid ID
        retrieved = service.get_or_404(created.id)
        assert retrieved is not None

        # Cleanup
        service.delete(created.id)


@pytest.mark.integration
def test_multiple_depositions_crud(test_client):
    """Test CRUD operations with multiple depositions."""
    with test_client.application.app_context():
        service = FakenodoService()

        initial_count = service.count()

        # Create multiple depositions
        dep1 = service.create(dep_metadata={"title": "Deposition 1"}, status="draft")
        dep2 = service.create(dep_metadata={"title": "Deposition 2"}, status="published")
        dep3 = service.create(dep_metadata={"title": "Deposition 3"}, status="draft")

        # Verify count increased
        assert service.count() == initial_count + 3

        # Update one
        service.update(dep2.id, status="draft")
        updated = service.get_by_id(dep2.id)
        assert updated.status == "draft"

        # Delete all
        service.delete(dep1.id)
        service.delete(dep2.id)
        service.delete(dep3.id)

        # Verify count back to initial
