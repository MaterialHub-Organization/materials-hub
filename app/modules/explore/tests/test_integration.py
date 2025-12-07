"""
Integration tests for explore module.
"""

import pytest

from app.modules.dataset.models import PublicationType
from app.modules.explore.services import ExploreService


@pytest.mark.integration
def test_explore_index_page_loads(test_client):
    """
    Test that the explore page loads successfully.
    """
    response = test_client.get("/explore")
    assert response.status_code == 200


@pytest.mark.integration
def test_explore_search_by_query(test_client, integration_test_data):
    """
    Test searching datasets by query string.
    """
    with test_client.application.app_context():
        service = ExploreService()

        # Search for "machine learning"
        results = service.filter(query="machine learning")
        assert len(results) >= 1
        assert any("Machine Learning" in ds.ds_meta_data.title for ds in results)


@pytest.mark.integration
def test_explore_search_by_author_name(test_client, integration_test_data):
    """
    Test searching datasets by author name.
    """
    with test_client.application.app_context():
        service = ExploreService()

        # Search for author "Jane Smith"
        results = service.filter(query="Jane Smith")
        assert len(results) >= 1
        assert any(any(author.name == "Jane Smith" for author in ds.ds_meta_data.authors) for ds in results)


@pytest.mark.integration
def test_explore_search_by_affiliation(test_client, integration_test_data):
    """
    Test searching datasets by author affiliation.
    """
    with test_client.application.app_context():
        service = ExploreService()

        # Search for affiliation "MIT"
        results = service.filter(query="MIT")
        assert len(results) >= 1
        assert any(any(author.affiliation == "MIT" for author in ds.ds_meta_data.authors) for ds in results)


@pytest.mark.integration
def test_explore_filter_by_publication_type(test_client, integration_test_data):
    """
    Test filtering datasets by publication type.
    """
    with test_client.application.app_context():
        service = ExploreService()

        # Filter by conference paper
        results = service.filter(query="", publication_type="conferencepaper")
        assert len(results) >= 1
        assert all(ds.ds_meta_data.publication_type == PublicationType.CONFERENCE_PAPER for ds in results)


@pytest.mark.integration
def test_explore_filter_by_tags(test_client, integration_test_data):
    """
    Test filtering datasets by tags.
    """
    with test_client.application.app_context():
        service = ExploreService()

        # Filter by tag "patterns"
        results = service.filter(query="", tags=["patterns"])
        assert len(results) >= 1
        assert all("patterns" in ds.ds_meta_data.tags.lower() for ds in results)


@pytest.mark.integration
def test_explore_sorting_newest(test_client, integration_test_data):
    """
    Test sorting datasets by newest first.
    """
    with test_client.application.app_context():
        service = ExploreService()

        results = service.filter(query="", sorting="newest")
        assert len(results) >= 2

        # Verify descending order
        for i in range(len(results) - 1):
            assert results[i].created_at >= results[i + 1].created_at


@pytest.mark.integration
def test_explore_sorting_oldest(test_client, integration_test_data):
    """
    Test sorting datasets by oldest first.
    """
    with test_client.application.app_context():
        service = ExploreService()

        results = service.filter(query="", sorting="oldest")
        assert len(results) >= 2

        # Verify ascending order
        for i in range(len(results) - 1):
            assert results[i].created_at <= results[i + 1].created_at


@pytest.mark.integration
def test_explore_combined_filters(test_client, integration_test_data):
    """
    Test using multiple filters together.
    """
    with test_client.application.app_context():
        service = ExploreService()

        # Search with query, publication type, and tags
        results = service.filter(query="software", publication_type="conferencepaper", tags=["patterns"])
        assert len(results) >= 1
        assert all(ds.ds_meta_data.publication_type == PublicationType.CONFERENCE_PAPER for ds in results)


@pytest.mark.integration
def test_explore_api_endpoint(test_client, integration_test_data):
    """
    Test the explore API endpoint returns JSON results.
    """
    response = test_client.post(
        "/explore",
        json={"query": "machine", "sorting": "newest", "publication_type": "any", "tags": []},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) >= 1


@pytest.mark.integration
def test_explore_pagination(test_client, integration_test_data):
    """Test explore page pagination."""
    response = test_client.get("/explore", query_string={"page": 1})
    assert response.status_code == 200


@pytest.mark.integration
def test_explore_empty_query(test_client, integration_test_data):
    """Test explore with empty query returns all datasets."""
    with test_client.application.app_context():
        service = ExploreService()
        results = service.filter(query="")
        assert len(results) >= 1


@pytest.mark.integration
def test_explore_repository_count(test_client, integration_test_data):
    """Test getting total dataset count."""
    with test_client.application.app_context():
        service = ExploreService()
        count = service.repository.count()
        assert count >= 3


@pytest.mark.integration
def test_explore_no_results_query(test_client):
    """Test explore with query that returns no results."""
    with test_client.application.app_context():
        service = ExploreService()
        results = service.filter(query="xyznonexistentquery123")
        assert len(results) == 0


@pytest.mark.integration
def test_explore_http_post_with_filters(test_client, integration_test_data):
    """Test explore HTTP POST endpoint with filters."""
    response = test_client.post(
        "/explore",
        json={"query": "", "sorting": "oldest", "publication_type": "any", "tags": []},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert isinstance(response.json, list)


@pytest.mark.integration
def test_explore_with_query_parameter(test_client):
    """Test explore GET with query parameter."""
    response = test_client.get("/explore?query=software")
    assert response.status_code == 200


@pytest.mark.integration
def test_explore_post_empty_json(test_client):
    """Test explore POST with empty JSON."""
    response = test_client.post("/explore", json={}, content_type="application/json")
    assert response.status_code == 200
    assert isinstance(response.json, list)


@pytest.mark.integration
def test_explore_post_with_tags(test_client):
    """Test explore POST with tags filter."""
    response = test_client.post("/explore", json={"tags": ["test"]}, content_type="application/json")
    assert response.status_code == 200
    assert isinstance(response.json, list)


@pytest.mark.integration
def test_explore_post_with_publication_type(test_client):
    """Test explore POST with publication type filter."""
    response = test_client.post(
        "/explore", json={"publication_type": "conferencepaper"}, content_type="application/json"
    )
    assert response.status_code == 200
    assert isinstance(response.json, list)


@pytest.mark.integration
def test_explore_service_repository_initialization(test_client):
    """Test ExploreService repository initialization."""
    with test_client.application.app_context():
        service = ExploreService()
        assert service.repository is not None


@pytest.mark.integration
def test_explore_service_filter_empty_results(test_client):
    """Test explore service filter returns empty list for no results."""
    with test_client.application.app_context():
        service = ExploreService()
        results = service.filter(query="nonexistent12345xyz")
        assert isinstance(results, list)
        assert len(results) == 0


@pytest.mark.integration
def test_explore_service_filter_by_multiple_tags(test_client, integration_test_data):
    """Test filtering by multiple tags."""
    with test_client.application.app_context():
        service = ExploreService()
        results = service.filter(query="", tags=["patterns", "software"])
        assert isinstance(results, list)


@pytest.mark.integration
def test_explore_route_returns_html(test_client):
    """Test that explore route GET returns HTML."""
    response = test_client.get("/explore")
    assert response.status_code == 200
    assert b"html" in response.data or b"<!DOCTYPE" in response.data or b"<div" in response.data


@pytest.mark.integration
def test_explore_post_sorting_by_views(test_client):
    """Test explore POST with sorting by views."""
    response = test_client.post("/explore", json={"sorting": "views"}, content_type="application/json")
    assert response.status_code == 200


@pytest.mark.integration
def test_explore_post_sorting_by_downloads(test_client):
    """Test explore POST with sorting by downloads."""
    response = test_client.post("/explore", json={"sorting": "downloads"}, content_type="application/json")
    assert response.status_code == 200


@pytest.mark.integration
def test_explore_dataset_metadata_in_results(test_client, integration_test_data):
    """Test that dataset metadata is included in results."""
    with test_client.application.app_context():
        service = ExploreService()
        results = service.filter(query="")
        if len(results) > 0:
            dataset = results[0]
            assert hasattr(dataset, 'ds_meta_data')
            assert dataset.ds_meta_data is not None


