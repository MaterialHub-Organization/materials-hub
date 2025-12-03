"""
Unit tests for explore module.
"""

import pytest

from app.modules.explore.repositories import ExploreRepository
from app.modules.explore.services import ExploreService


@pytest.mark.unit
def test_explore_repository_initialization(test_client):
    """Test ExploreRepository initialization."""
    repository = ExploreRepository()
    assert repository.model.__name__ == "MaterialsDataset"


@pytest.mark.unit
def test_explore_service_initialization(test_client):
    """Test ExploreService initialization."""
    service = ExploreService()
    assert isinstance(service.repository, ExploreRepository)


@pytest.mark.unit
def test_explore_service_filter_calls_repository(test_client):
    """Test that ExploreService.filter calls repository.filter."""
    service = ExploreService()

    # Mock the repository filter method
    original_filter = service.repository.filter
    call_count = [0]

    def mock_filter(*args, **kwargs):
        call_count[0] += 1
        return []

    service.repository.filter = mock_filter

    # Call the service filter method
    result = service.filter(query="test", sorting="newest", publication_type="any", tags=[])

    # Verify the repository method was called
    assert call_count[0] == 1
    assert result == []

    # Restore original method
    service.repository.filter = original_filter
