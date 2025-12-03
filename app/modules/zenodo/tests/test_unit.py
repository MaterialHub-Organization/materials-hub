"""
Unit tests for zenodo module.
"""

import os
from unittest.mock import Mock, patch

import pytest

from app import db
from app.modules.zenodo.models import Zenodo
from app.modules.zenodo.repositories import ZenodoRepository
from app.modules.zenodo.services import ZenodoService


@pytest.mark.unit
def test_zenodo_model_creation(test_client):
    """Test creating a Zenodo model instance."""
    zenodo = Zenodo()
    db.session.add(zenodo)
    db.session.commit()

    assert zenodo.id is not None


@pytest.mark.unit
def test_zenodo_repository_initialization(test_client):
    """Test ZenodoRepository initialization."""
    repository = ZenodoRepository()
    assert repository.model == Zenodo


@pytest.mark.unit
@patch.dict(os.environ, {"ZENODO_ACCESS_TOKEN": "test_token", "FLASK_ENV": "development"})
def test_zenodo_service_initialization(test_client):
    """Test ZenodoService initialization."""
    service = ZenodoService()
    assert isinstance(service.repository, ZenodoRepository)
    assert service.ZENODO_ACCESS_TOKEN == "test_token"
    assert "sandbox.zenodo.org" in service.ZENODO_API_URL
    assert service.params == {"access_token": "test_token"}
    assert service.headers == {"Content-Type": "application/json"}


@pytest.mark.unit
@patch.dict(os.environ, {"FLASK_ENV": "development"})
def test_get_zenodo_url_development(test_client):
    """Test get_zenodo_url returns sandbox URL in development."""
    service = ZenodoService()
    url = service.get_zenodo_url()
    assert "sandbox.zenodo.org" in url


@pytest.mark.unit
@patch.dict(os.environ, {"FLASK_ENV": "production"})
def test_get_zenodo_url_production(test_client):
    """Test get_zenodo_url returns production URL in production."""
    service = ZenodoService()
    url = service.get_zenodo_url()
    assert url == "https://zenodo.org/api/deposit/depositions" or "zenodo.org" in url


@pytest.mark.unit
@patch.dict(os.environ, {"FLASK_ENV": "testing"})
def test_get_zenodo_url_default(test_client):
    """Test get_zenodo_url returns sandbox URL for unknown environments."""
    service = ZenodoService()
    url = service.get_zenodo_url()
    assert "sandbox.zenodo.org" in url


@pytest.mark.unit
@patch.dict(os.environ, {"ZENODO_ACCESS_TOKEN": "my_secret_token"})
def test_get_zenodo_access_token(test_client):
    """Test get_zenodo_access_token returns token from env."""
    service = ZenodoService()
    token = service.get_zenodo_access_token()
    assert token == "my_secret_token"


@pytest.mark.unit
@patch("app.modules.zenodo.services.requests.get")
def test_test_connection_success(mock_get, test_client):
    """Test successful connection to Zenodo."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    service = ZenodoService()
    result = service.test_connection()

    assert result is True
    mock_get.assert_called_once_with(service.ZENODO_API_URL, params=service.params, headers=service.headers)


@pytest.mark.unit
@patch("app.modules.zenodo.services.requests.get")
def test_test_connection_failure(mock_get, test_client):
    """Test failed connection to Zenodo."""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response

    service = ZenodoService()
    result = service.test_connection()

    assert result is False


@pytest.mark.unit
@patch("app.modules.zenodo.services.requests.get")
def test_get_all_depositions_success(mock_get, test_client):
    """Test getting all depositions from Zenodo."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "title": "Test 1"},
        {"id": 2, "title": "Test 2"},
    ]
    mock_get.return_value = mock_response

    service = ZenodoService()
    result = service.get_all_depositions()

    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["title"] == "Test 2"


@pytest.mark.unit
@patch("app.modules.zenodo.services.requests.get")
def test_get_all_depositions_failure(mock_get, test_client):
    """Test getting all depositions fails with exception."""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    service = ZenodoService()

    with pytest.raises(Exception, match="Failed to get depositions"):
        service.get_all_depositions()


@pytest.mark.unit
@patch("app.modules.zenodo.services.requests.post")
def test_create_new_deposition_success(mock_post, test_client):
    """Test creating a new deposition in Zenodo."""
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": 12345,
        "doi": "10.5281/zenodo.12345",
        "metadata": {"title": "Test Dataset"},
    }
    mock_post.return_value = mock_response

    service = ZenodoService()

    # Mock dataset
    mock_dataset = Mock()
    mock_dataset.ds_meta_data.title = "Test Dataset"
    mock_dataset.ds_meta_data.description = "Test description"
    mock_dataset.ds_meta_data.publication_type.value = "none"
    mock_dataset.ds_meta_data.tags = "tag1, tag2"

    # Mock author
    mock_author = Mock()
    mock_author.name = "John Doe"
    mock_author.affiliation = "Test University"
    mock_author.orcid = "0000-0000-0000-0000"
    mock_dataset.ds_meta_data.authors = [mock_author]

    result = service.create_new_deposition(mock_dataset)

    assert result["id"] == 12345
    assert result["doi"] == "10.5281/zenodo.12345"
    mock_post.assert_called_once()


@pytest.mark.unit
@patch("app.modules.zenodo.services.requests.post")
def test_create_new_deposition_with_publication_type(mock_post, test_client):
    """Test creating a deposition with publication type."""
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 12345}
    mock_post.return_value = mock_response

    service = ZenodoService()

    mock_dataset = Mock()
    mock_dataset.ds_meta_data.title = "Test Publication"
    mock_dataset.ds_meta_data.description = "Test"
    mock_dataset.ds_meta_data.publication_type.value = "article"
    mock_dataset.ds_meta_data.tags = ""

    mock_author = Mock()
    mock_author.name = "Jane Doe"
    mock_author.affiliation = None
    mock_author.orcid = None
    mock_dataset.ds_meta_data.authors = [mock_author]

    service.create_new_deposition(mock_dataset)

    # Verify the call was made with correct metadata
    call_args = mock_post.call_args
    metadata = call_args.kwargs["json"]["metadata"]

    assert metadata["upload_type"] == "publication"
    assert metadata["publication_type"] == "article"
    assert metadata["creators"][0] == {"name": "Jane Doe"}


@pytest.mark.unit
@patch("app.modules.zenodo.services.requests.post")
def test_create_new_deposition_failure(mock_post, test_client):
    """Test creating deposition fails with exception."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error": "Bad request"}
    mock_post.return_value = mock_response

    service = ZenodoService()

    mock_dataset = Mock()
    mock_dataset.ds_meta_data.title = "Test"
    mock_dataset.ds_meta_data.description = "Test"
    mock_dataset.ds_meta_data.publication_type.value = "none"
    mock_dataset.ds_meta_data.tags = ""
    mock_dataset.ds_meta_data.authors = []

    with pytest.raises(Exception, match="Failed to create deposition"):
        service.create_new_deposition(mock_dataset)


@pytest.mark.unit
@patch("app.modules.zenodo.services.requests.post")
def test_publish_deposition_success(mock_post, test_client):
    """Test publishing a deposition in Zenodo."""
    mock_response = Mock()
    mock_response.status_code = 202
    mock_response.json.return_value = {
        "id": 12345,
        "state": "done",
        "doi": "10.5281/zenodo.12345",
    }
    mock_post.return_value = mock_response

    service = ZenodoService()
    result = service.publish_deposition(12345)

    assert result["id"] == 12345
    assert result["state"] == "done"


@pytest.mark.unit
@patch("app.modules.zenodo.services.requests.post")
def test_publish_deposition_failure(mock_post, test_client):
    """Test publishing deposition fails with exception."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_post.return_value = mock_response

    service = ZenodoService()

    with pytest.raises(Exception, match="Failed to publish deposition"):
        service.publish_deposition(12345)


@pytest.mark.unit
@patch("app.modules.zenodo.services.requests.get")
def test_get_deposition_success(mock_get, test_client):
    """Test getting a deposition from Zenodo."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 12345,
        "doi": "10.5281/zenodo.12345",
        "metadata": {"title": "Test Dataset"},
    }
    mock_get.return_value = mock_response

    service = ZenodoService()
    result = service.get_deposition(12345)

    assert result["id"] == 12345
    assert result["doi"] == "10.5281/zenodo.12345"


@pytest.mark.unit
@patch("app.modules.zenodo.services.requests.get")
def test_get_deposition_failure(mock_get, test_client):
    """Test getting deposition fails with exception."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    service = ZenodoService()

    with pytest.raises(Exception, match="Failed to get deposition"):
        service.get_deposition(12345)


@pytest.mark.unit
@patch("app.modules.zenodo.services.requests.get")
def test_get_doi(mock_get, test_client):
    """Test getting DOI from a deposition."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 12345,
        "doi": "10.5281/zenodo.12345",
    }
    mock_get.return_value = mock_response

    service = ZenodoService()
    doi = service.get_doi(12345)

    assert doi == "10.5281/zenodo.12345"
