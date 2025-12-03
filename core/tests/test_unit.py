"""
Unit tests for core module (BaseRepository and BaseService).
"""

import pytest

from app import db
from app.modules.zenodo.models import Zenodo
from core.repositories.BaseRepository import BaseRepository
from core.services.BaseService import BaseService


@pytest.mark.unit
def test_base_repository_initialization(test_client):
    """Test BaseRepository initialization."""
    repository = BaseRepository(Zenodo)
    assert repository.model == Zenodo
    assert repository.session == db.session


@pytest.mark.unit
def test_base_repository_create(test_client):
    """Test BaseRepository create method."""
    repository = BaseRepository(Zenodo)
    instance = repository.create()

    assert instance.id is not None
    assert isinstance(instance, Zenodo)


@pytest.mark.unit
def test_base_repository_create_no_commit(test_client):
    """Test BaseRepository create method without committing."""
    repository = BaseRepository(Zenodo)
    instance = repository.create(commit=False)

    # Instance should exist but not be committed yet
    assert instance is not None
    db.session.commit()  # Commit manually
    assert instance.id is not None


@pytest.mark.unit
def test_base_repository_get_by_id(test_client):
    """Test BaseRepository get_by_id method."""
    repository = BaseRepository(Zenodo)
    created = repository.create()

    retrieved = repository.get_by_id(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id


@pytest.mark.unit
def test_base_repository_get_by_id_not_found(test_client):
    """Test BaseRepository get_by_id with non-existent ID."""
    repository = BaseRepository(Zenodo)
    result = repository.get_by_id(99999)

    assert result is None


@pytest.mark.unit
def test_base_repository_count(test_client):
    """Test BaseRepository count method."""
    repository = BaseRepository(Zenodo)

    initial_count = repository.count()
    repository.create()
    repository.create()

    final_count = repository.count()

    assert final_count == initial_count + 2


@pytest.mark.unit
def test_base_repository_update(test_client):
    """Test BaseRepository update method."""
    repository = BaseRepository(Zenodo)
    instance = repository.create()

    # Zenodo model only has id, so we can't update other fields
    # This test just verifies the update method works
    updated = repository.update(instance.id)

    assert updated is not None
    assert updated.id == instance.id


@pytest.mark.unit
def test_base_repository_update_not_found(test_client):
    """Test BaseRepository update with non-existent ID."""
    repository = BaseRepository(Zenodo)
    result = repository.update(99999)

    assert result is None


@pytest.mark.unit
def test_base_repository_delete(test_client):
    """Test BaseRepository delete method."""
    repository = BaseRepository(Zenodo)
    instance = repository.create()
    instance_id = instance.id

    result = repository.delete(instance_id)

    assert result is True
    assert repository.get_by_id(instance_id) is None


@pytest.mark.unit
def test_base_repository_delete_not_found(test_client):
    """Test BaseRepository delete with non-existent ID."""
    repository = BaseRepository(Zenodo)
    result = repository.delete(99999)

    assert result is False


@pytest.mark.unit
def test_base_service_initialization(test_client):
    """Test BaseService initialization."""
    repository = BaseRepository(Zenodo)
    service = BaseService(repository)

    assert service.repository == repository


@pytest.mark.unit
def test_base_service_create(test_client):
    """Test BaseService create method."""
    repository = BaseRepository(Zenodo)
    service = BaseService(repository)

    instance = service.create()

    assert instance.id is not None
    assert isinstance(instance, Zenodo)


@pytest.mark.unit
def test_base_service_get_by_id(test_client):
    """Test BaseService get_by_id method."""
    repository = BaseRepository(Zenodo)
    service = BaseService(repository)

    created = service.create()
    retrieved = service.get_by_id(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id


@pytest.mark.unit
def test_base_service_count(test_client):
    """Test BaseService count method."""
    repository = BaseRepository(Zenodo)
    service = BaseService(repository)

    initial_count = service.count()
    service.create()
    service.create()

    final_count = service.count()

    assert final_count == initial_count + 2


@pytest.mark.unit
def test_base_service_update(test_client):
    """Test BaseService update method."""
    repository = BaseRepository(Zenodo)
    service = BaseService(repository)

    instance = service.create()
    updated = service.update(instance.id)

    assert updated is not None
    assert updated.id == instance.id


@pytest.mark.unit
def test_base_service_delete(test_client):
    """Test BaseService delete method."""
    repository = BaseRepository(Zenodo)
    service = BaseService(repository)

    instance = service.create()
    instance_id = instance.id

    result = service.delete(instance_id)

    assert result is True
    assert service.get_by_id(instance_id) is None


@pytest.mark.unit
def test_base_service_get_or_404(test_client):
    """Test BaseService get_or_404 method."""
    repository = BaseRepository(Zenodo)
    service = BaseService(repository)

    instance = service.create()
    retrieved = service.get_or_404(instance.id)

    assert retrieved is not None
    assert retrieved.id == instance.id
