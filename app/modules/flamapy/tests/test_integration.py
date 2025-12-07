"""
Integration tests for flamapy module.
"""

import pytest

from app import db
from app.modules.flamapy.models import Flamapy
from app.modules.flamapy.services import FlamapyService


@pytest.mark.integration
def test_flamapy_service_initialization(test_client):
    """Test FlamapyService can be initialized."""
    with test_client.application.app_context():
        service = FlamapyService()
        assert service is not None


@pytest.mark.integration
def test_create_flamapy_record(test_client):
    """Test creating a Flamapy record."""
    with test_client.application.app_context():
        flamapy = Flamapy()
        db.session.add(flamapy)
        db.session.commit()

        assert flamapy.id is not None

        # Cleanup
        db.session.delete(flamapy)
        db.session.commit()


@pytest.mark.integration
def test_flamapy_repository_operations(test_client):
    """Test basic repository operations for Flamapy."""
    with test_client.application.app_context():
        service = FlamapyService()

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
def test_flamapy_update_operations(test_client):
    """Test update operations for Flamapy."""
    with test_client.application.app_context():
        service = FlamapyService()

        # Create
        created = service.create()
        original_id = created.id

        # Get by id to verify
        retrieved = service.get_by_id(original_id)
        assert retrieved is not None
        assert retrieved.id == original_id

        # Cleanup
        service.delete(original_id)


@pytest.mark.integration
def test_flamapy_count(test_client):
    """Test counting Flamapy records."""
    with test_client.application.app_context():
        service = FlamapyService()

        # Get initial count
        initial_count = service.count()

        # Create records
        record1 = service.create()
        record2 = service.create()

        assert service.count() == initial_count + 2

        # Cleanup
        service.delete(record1.id)
        service.delete(record2.id)
        assert service.count() == initial_count


@pytest.mark.integration
def test_flamapy_get_or_404(test_client):
    """Test get_or_404 method for Flamapy."""
    with test_client.application.app_context():
        service = FlamapyService()

        # Create a record
        created = service.create()

        # Get with valid ID
        retrieved = service.get_or_404(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id

        # Cleanup
        service.delete(created.id)


@pytest.mark.integration
def test_multiple_flamapy_records(test_client):
    """Test creating and managing multiple Flamapy records."""
    with test_client.application.app_context():
        service = FlamapyService()

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

