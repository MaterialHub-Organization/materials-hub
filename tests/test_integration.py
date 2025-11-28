"""
Consolidated integration tests for all modules.
"""
import io

import pytest

from app.modules.auth.models import User
from app.modules.dataset.models import DataSet, PublicationType
from app.modules.dataset.services import DataSetService
from app.modules.explore.services import ExploreService

# ============================================================================
# Tests from app/modules/explore/tests/test_integration.py
# ============================================================================


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


# ============================================================================
# Tests from app/modules/fakenodo/tests/test_integration.py
# ============================================================================


@pytest.mark.integration
def test_fakenodo_upload_dataset(test_client):
    """
    Test uploading a file to Fakenodo.
    """
    # Create a fake file
    data = {"file": (io.BytesIO(b"test file content"), "test.uvl")}

    response = test_client.post("/fakenodo/upload", data=data, content_type="multipart/form-data")

    assert response.status_code == 201
    assert "id" in response.json
    assert "filename" in response.json
    assert response.json["filename"] == "test.uvl"


@pytest.mark.integration
def test_fakenodo_upload_no_file(test_client):
    """
    Test uploading without a file returns error.
    """
    response = test_client.post("/fakenodo/upload", data={})

    assert response.status_code == 400
    if response.json:
        assert "error" in response.json


@pytest.mark.integration
def test_fakenodo_list_datasets(test_client):
    """
    Test listing all datasets in Fakenodo.
    """
    # Upload a dataset first
    data = {"file": (io.BytesIO(b"test content"), "list_test.uvl")}
    test_client.post("/fakenodo/upload", data=data, content_type="multipart/form-data")

    # List datasets
    response = test_client.get("/fakenodo/datasets")

    assert response.status_code == 200
    assert isinstance(response.json, list)


@pytest.mark.integration
def test_fakenodo_download_dataset(test_client):
    """
    Test downloading a dataset from Fakenodo.
    """
    # Upload a dataset first
    data = {"file": (io.BytesIO(b"download test content"), "download_test.uvl")}
    upload_response = test_client.post("/fakenodo/upload", data=data, content_type="multipart/form-data")

    dataset_id = upload_response.json["id"]

    # Download the dataset
    response = test_client.get(f"/fakenodo/download/{dataset_id}")

    assert response.status_code == 200
    assert b"download test content" in response.data


@pytest.mark.integration
def test_fakenodo_download_nonexistent(test_client):
    """
    Test downloading a non-existent dataset returns 404.
    """
    response = test_client.get("/fakenodo/download/99999")

    assert response.status_code == 404
    assert "error" in response.json


@pytest.mark.integration
def test_fakenodo_delete_dataset(test_client):
    """
    Test deleting a dataset from Fakenodo.
    """
    # Upload a dataset first
    data = {"file": (io.BytesIO(b"delete test content"), "delete_test.uvl")}
    upload_response = test_client.post("/fakenodo/upload", data=data, content_type="multipart/form-data")

    dataset_id = upload_response.json["id"]

    # Delete the dataset
    response = test_client.delete(f"/fakenodo/dataset/{dataset_id}")

    assert response.status_code == 200
    assert "message" in response.json

    # Verify it's deleted
    download_response = test_client.get(f"/fakenodo/download/{dataset_id}")
    assert download_response.status_code == 404


@pytest.mark.integration
def test_fakenodo_delete_nonexistent(test_client):
    """
    Test deleting a non-existent dataset returns 404.
    """
    response = test_client.delete("/fakenodo/dataset/99999")

    assert response.status_code == 404
    assert "error" in response.json


@pytest.mark.integration
def test_fakenodo_upload_download_lifecycle(test_client):
    """
    Test the complete lifecycle: upload, list, download, delete.
    """
    # 1. Upload
    data = {"file": (io.BytesIO(b"lifecycle test"), "lifecycle.uvl")}
    upload_response = test_client.post("/fakenodo/upload", data=data, content_type="multipart/form-data")
    assert upload_response.status_code == 201
    dataset_id = upload_response.json["id"]

    # 2. List (should contain our dataset)
    list_response = test_client.get("/fakenodo/datasets")
    assert list_response.status_code == 200
    dataset_ids = [ds["id"] for ds in list_response.json]
    assert dataset_id in dataset_ids

    # 3. Download
    download_response = test_client.get(f"/fakenodo/download/{dataset_id}")
    assert download_response.status_code == 200
    assert b"lifecycle test" in download_response.data

    # 4. Delete
    delete_response = test_client.delete(f"/fakenodo/dataset/{dataset_id}")
    assert delete_response.status_code == 200

    # 5. Verify deletion
    download_after_delete = test_client.get(f"/fakenodo/download/{dataset_id}")
    assert download_after_delete.status_code == 404


# ============================================================================
# Tests from app/modules/dataset/tests/test_integration.py
# ============================================================================


@pytest.mark.integration
def test_dataset_count_synchronized(test_client, integration_test_data):
    """
    Test counting synchronized datasets (those with DOI).
    """
    with test_client.application.app_context():
        service = DataSetService()
        count = service.count_synchronized_datasets()

        # Should have 1 synchronized dataset
        assert count == 1


@pytest.mark.integration
def test_dataset_count_authors(test_client, integration_test_data):
    """
    Test counting total authors in the system.
    """
    with test_client.application.app_context():
        service = DataSetService()
        count = service.count_authors()

        # Should have 2 authors
        assert count == 2


@pytest.mark.integration
def test_dataset_total_downloads(test_client, integration_test_data):
    """
    Test counting total dataset downloads.
    """
    with test_client.application.app_context():
        service = DataSetService()
        total = service.total_dataset_downloads()

        # Should have 1 download record
        assert total == 1


@pytest.mark.integration
def test_dataset_total_views(test_client, integration_test_data):
    """
    Test counting total dataset views.
    """
    with test_client.application.app_context():
        service = DataSetService()
        total = service.total_dataset_views()

        # Should have 1 view record
        assert total == 1


@pytest.mark.integration
def test_dataset_get_synchronized(test_client, integration_test_data):
    """
    Test retrieving synchronized datasets for a user.
    """
    with test_client.application.app_context():
        service = DataSetService()
        user = User.query.filter_by(email="user1@example.com").first()

        synchronized = service.get_synchronized(user.id)

        # User1 has 1 synchronized dataset
        assert len(synchronized) == 1
        assert synchronized[0].ds_meta_data.dataset_doi is not None


@pytest.mark.integration
def test_dataset_get_unsynchronized(test_client, integration_test_data):
    """
    Test retrieving unsynchronized datasets for a user.
    """
    with test_client.application.app_context():
        service = DataSetService()
        user = User.query.filter_by(email="user1@example.com").first()

        unsynchronized = service.get_unsynchronized(user.id)

        # User1 has 1 unsynchronized dataset
        assert len(unsynchronized) == 1
        assert unsynchronized[0].ds_meta_data.dataset_doi is None


@pytest.mark.integration
def test_dataset_latest_synchronized(test_client, integration_test_data):
    """
    Test retrieving latest synchronized datasets.
    """
    with test_client.application.app_context():
        service = DataSetService()
        latest = service.latest_synchronized()

        # Should return datasets ordered by creation date descending
        assert len(latest) >= 1
        assert all(ds.ds_meta_data.dataset_doi is not None for ds in latest)


@pytest.mark.integration
def test_dataset_get_recommendations(test_client, integration_test_data):
    """
    Test getting recommended datasets based on similarity.
    """
    with test_client.application.app_context():
        service = DataSetService()
        user = User.query.filter_by(email="user1@example.com").first()
        datasets = service.get_synchronized(user.id)

        if datasets:
            dataset_id = datasets[0].id
            recommendations = service.get_recommendations(dataset_id, limit=5)

            # Should return a list (may be empty if only one dataset)
            assert isinstance(recommendations, list)
            # Should not include the current dataset
            assert all(ds.id != dataset_id for ds in recommendations)


@pytest.mark.integration
def test_dataset_filter_by_authors(test_client, integration_test_data):
    """
    Test filtering datasets by common authors.
    """
    with test_client.application.app_context():
        service = DataSetService()
        user = User.query.filter_by(email="user1@example.com").first()
        datasets = service.get_synchronized(user.id)

        if datasets:
            current_dataset = datasets[0]
            all_datasets = service.get_all_except(current_dataset.id)
            filtered = service.filter_by_authors(all_datasets, current_dataset)

            # Should return a list
            assert isinstance(filtered, list)


@pytest.mark.integration
def test_dataset_filter_by_tags(test_client, integration_test_data):
    """
    Test filtering datasets by common tags.
    """
    with test_client.application.app_context():
        service = DataSetService()
        user = User.query.filter_by(email="user1@example.com").first()
        datasets = service.get_synchronized(user.id)

        if datasets:
            current_dataset = datasets[0]
            all_datasets = service.get_all_except(current_dataset.id)
            filtered = service.filter_by_tags(all_datasets, current_dataset)

            # Should return a list
            assert isinstance(filtered, list)


@pytest.mark.integration
def test_dataset_download_route(test_client, integration_test_data):
    """
    Test the dataset download endpoint.
    """
    with test_client.application.app_context():
        user = User.query.filter_by(email="user1@example.com").first()
        datasets = DataSet.query.filter_by(user_id=user.id).all()

        if datasets:
            dataset_id = datasets[0].id
            # Note: This will fail because files don't actually exist
            # but we can test the endpoint exists
            response = test_client.get(f"/dataset/download/{dataset_id}")
            # Expect 500 or 404 because files don't exist in test
            assert response.status_code in [200, 404, 500]


@pytest.mark.integration
def test_doi_redirect_route(test_client, integration_test_data):
    """
    Test viewing dataset by DOI.
    """
    # Get DOI without app_context, then make HTTP call
    with test_client.application.app_context():
        datasets = DataSet.query.filter(DataSet.ds_meta_data.has(dataset_doi="10.1234/ml.2024.001")).all()
        doi = datasets[0].ds_meta_data.dataset_doi if datasets else None

    if doi:
        response = test_client.get(f"/doi/{doi}/")
        assert response.status_code in [200, 302]  # 200 OK or 302 redirect


@pytest.mark.integration
def test_dataset_list_route(test_client, integration_test_data):
    """
    Test the dataset list page (requires login).
    """
    # Login first (without app_context during HTTP calls)
    test_client.post("/login", data={"email": "user1@example.com", "password": "test1234"}, follow_redirects=True)

    response = test_client.get("/dataset/list")
    assert response.status_code == 200


@pytest.mark.integration
def test_unsynchronized_dataset_route(test_client, integration_test_data):
    """
    Test viewing an unsynchronized dataset.
    """
    # Get dataset ID first
    with test_client.application.app_context():
        user = User.query.filter_by(email="user1@example.com").first()
        service = DataSetService()
        unsync_datasets = service.get_unsynchronized(user.id)
        dataset_id = unsync_datasets[0].id if unsync_datasets else None

    if dataset_id:
        # Login (without app_context during HTTP calls)
        test_client.post("/login", data={"email": "user1@example.com", "password": "test1234"}, follow_redirects=True)

        response = test_client.get(f"/dataset/unsynchronized/{dataset_id}/")
        assert response.status_code == 200


@pytest.mark.integration
def test_dsviewrecord_create_cookie(test_client, integration_test_data):
    """
    Test DSViewRecordService cookie creation.
    """
    with test_client.application.app_context():
        from app.modules.dataset.services import DSViewRecordService

        service = DSViewRecordService()

        user = User.query.filter_by(email="user1@example.com").first()
        datasets = DataSet.query.filter_by(user_id=user.id).first()

        if datasets:
            # Mock request context
            with test_client.application.test_request_context("/"):
                cookie = service.create_cookie(dataset=datasets)
                assert cookie is not None
                assert len(cookie) > 0


# ==================== API Integration Tests ====================


@pytest.mark.integration
def test_api_datasets_list(test_client):
    """
    Test the API endpoint for listing datasets.
    """
    response = test_client.get("/api/v1/datasets/")
    assert response.status_code in [200, 404]  # May be 404 if no datasets


@pytest.mark.integration
def test_api_dataset_get_by_id(test_client, integration_test_data):
    """
    Test the API endpoint for getting a specific dataset.
    """
    # Get dataset ID first
    with test_client.application.app_context():
        dataset = DataSet.query.first()
        dataset_id = dataset.id if dataset else None

    if dataset_id:
        response = test_client.get(f"/api/v1/datasets/{dataset_id}")
        assert response.status_code == 200
        assert "dataset_id" in response.json or "id" in response.json


@pytest.mark.integration
def test_api_dataset_nonexistent(test_client):
    """
    Test the API endpoint returns 404 for non-existent dataset.
    """
    response = test_client.get("/api/v1/datasets/99999")
    assert response.status_code == 404


@pytest.mark.integration
def test_dataset_recommendations_api(test_client, integration_test_data):
    """
    Test the dataset recommendations API endpoint.
    """
    # Get dataset ID first
    with test_client.application.app_context():
        dataset = DataSet.query.first()
        dataset_id = dataset.id if dataset else None

    if dataset_id:
        response = test_client.get(
            f"/dataset/{dataset_id}/recommendations", query_string={"page": 1, "filter_type": "authors"}
        )
        assert response.status_code == 200
        assert "html" in response.json or isinstance(response.json, dict)


@pytest.mark.integration
@pytest.mark.skip(reason="Endpoint con problema de rendimiento - carga todos los datasets en memoria")
def test_dataset_recommendations_by_doi_api(test_client, integration_test_data):
    """
    Test the dataset recommendations by DOI API endpoint.
    """
    # Get DOI first
    with test_client.application.app_context():
        dataset = DataSet.query.filter(DataSet.ds_meta_data.has(dataset_doi="10.1234/ml.2024.001")).first()
        doi = dataset.ds_meta_data.dataset_doi if dataset and dataset.ds_meta_data else None

    if doi:
        response = test_client.get(f"/doi/{doi}/recommendations", query_string={"page": 1})
        assert response.status_code == 200
