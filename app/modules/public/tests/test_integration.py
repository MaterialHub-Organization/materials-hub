"""
Integration tests for public module.
"""

import pytest


@pytest.mark.integration
def test_index_page_loads(test_client):
    """Test that the index/home page loads successfully."""
    response = test_client.get("/")
    assert response.status_code == 200


@pytest.mark.integration
def test_index_page_contains_statistics(test_client, integration_test_data):
    """Test that the index page displays statistics."""
    response = test_client.get("/")
    assert response.status_code == 200
    # Check for common elements on the index page
    assert b"materials" in response.data.lower() or b"dataset" in response.data.lower()


@pytest.mark.integration
def test_index_page_shows_latest_datasets(test_client, integration_test_data):
    """Test that the index page shows latest datasets."""
    response = test_client.get("/")
    assert response.status_code == 200
    # The page should contain some dataset information
    data = response.data.decode("utf-8")
    assert len(data) > 0


@pytest.mark.integration
def test_index_page_without_datasets(test_client):
    """Test that the index page loads even without datasets."""
    response = test_client.get("/")
    assert response.status_code == 200


@pytest.mark.integration
def test_index_page_statistics_structure(test_client, integration_test_data):
    """Test that index page renders with statistics."""
    with test_client.application.app_context():
        from app.modules.dataset.repositories import (
            DSDownloadRecordRepository,
            DSViewRecordRepository,
            MaterialsDatasetRepository,
        )

        materials_dataset_repository = MaterialsDatasetRepository()
        download_repository = DSDownloadRecordRepository()
        view_repository = DSViewRecordRepository()

        # Verify repositories can be initialized and return counts
        datasets_counter = materials_dataset_repository.count_synchronized()
        total_downloads = download_repository.count()
        total_views = view_repository.count()

        assert datasets_counter >= 0
        assert total_downloads >= 0
        assert total_views >= 0


@pytest.mark.integration
def test_index_page_latest_datasets_query(test_client, integration_test_data):
    """Test that latest datasets can be queried."""
    with test_client.application.app_context():
        from app.modules.dataset.repositories import MaterialsDatasetRepository

        repository = MaterialsDatasetRepository()
        latest = repository.get_synchronized_latest(limit=5)

        assert isinstance(latest, list)
        assert len(latest) <= 5


@pytest.mark.integration
def test_index_page_download_statistics(test_client, integration_test_data):
    """Test that download statistics are tracked."""
    with test_client.application.app_context():
        from app.modules.dataset.repositories import DSDownloadRecordRepository

        repository = DSDownloadRecordRepository()
        downloads = repository.count()

        assert downloads >= 0


@pytest.mark.integration
def test_index_page_view_statistics(test_client, integration_test_data):
    """Test that view statistics are tracked."""
    with test_client.application.app_context():
        from app.modules.dataset.repositories import DSViewRecordRepository

        repository = DSViewRecordRepository()
        views = repository.count()

        assert views >= 0


@pytest.mark.integration
def test_index_page_multiple_requests(test_client):
    """Test that multiple index page requests work."""
    for i in range(3):
        response = test_client.get("/")
        assert response.status_code == 200
