"""
Integration tests for hubfile module.
"""

import pytest

from app import db
from app.modules.dataset.models import PublicationType
from app.modules.featuremodel.models import FeatureModel, FMMetaData
from app.modules.hubfile.models import Hubfile, HubfileDownloadRecord, HubfileViewRecord
from app.modules.hubfile.services import HubfileService


@pytest.mark.integration
def test_hubfile_service_initialization(test_client):
    """Test HubfileService can be initialized."""
    with test_client.application.app_context():
        service = HubfileService()
        assert service is not None


@pytest.mark.integration
def test_create_hubfile(test_client):
    """Test creating a hubfile."""
    with test_client.application.app_context():
        # Create dependencies
        fm_metadata = FMMetaData(
            uvl_filename="integration_test.uvl",
            title="Integration Test FM",
            description="Test",
            publication_type=PublicationType.NONE,
        )
        db.session.add(fm_metadata)
        db.session.commit()

        feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
        db.session.add(feature_model)
        db.session.commit()

        # Create hubfile
        hubfile = Hubfile(name="test.uvl", checksum="abc123", size=1024, feature_model_id=feature_model.id)
        db.session.add(hubfile)
        db.session.commit()

        assert hubfile.id is not None
        assert hubfile.name == "test.uvl"

        # Cleanup - cascade delete will remove fm_metadata automatically
        db.session.delete(hubfile)
        db.session.commit()
        db.session.delete(feature_model)
        db.session.commit()


@pytest.mark.integration
def test_hubfile_view_record_creation(test_client):
    """Test creating a hubfile view record."""
    with test_client.application.app_context():
        # Create dependencies
        fm_metadata = FMMetaData(
            uvl_filename="view_test.uvl",
            title="View Test",
            description="Test",
            publication_type=PublicationType.NONE,
        )
        db.session.add(fm_metadata)
        db.session.commit()

        feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
        db.session.add(feature_model)
        db.session.commit()

        hubfile = Hubfile(name="view.uvl", checksum="def456", size=2048, feature_model_id=feature_model.id)
        db.session.add(hubfile)
        db.session.commit()

        # Create view record
        view_record = HubfileViewRecord(file_id=hubfile.id, view_cookie="test-cookie")
        db.session.add(view_record)
        db.session.commit()

        assert view_record.id is not None
        assert view_record.file_id == hubfile.id

        # Cleanup - delete in reverse order with commits to respect FK constraints
        # Cascade delete will remove fm_metadata automatically
        db.session.delete(view_record)
        db.session.commit()
        db.session.delete(hubfile)
        db.session.commit()
        db.session.delete(feature_model)
        db.session.commit()


@pytest.mark.integration
def test_hubfile_download_record_creation(test_client):
    """Test creating a hubfile download record."""
    with test_client.application.app_context():
        # Create dependencies
        fm_metadata = FMMetaData(
            uvl_filename="download_test.uvl",
            title="Download Test",
            description="Test",
            publication_type=PublicationType.NONE,
        )
        db.session.add(fm_metadata)
        db.session.commit()

        feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
        db.session.add(feature_model)
        db.session.commit()

        hubfile = Hubfile(name="download.uvl", checksum="ghi789", size=3072, feature_model_id=feature_model.id)
        db.session.add(hubfile)
        db.session.commit()

        # Create download record
        download_record = HubfileDownloadRecord(file_id=hubfile.id, download_cookie="download-cookie")
        db.session.add(download_record)
        db.session.commit()

        assert download_record.id is not None
        assert download_record.file_id == hubfile.id

        # Cleanup - delete in reverse order with commits to respect FK constraints
        # Cascade delete will remove fm_metadata automatically
        db.session.delete(download_record)
        db.session.commit()
        db.session.delete(hubfile)
        db.session.commit()
        db.session.delete(feature_model)
        db.session.commit()


@pytest.mark.integration
def test_hubfile_total_views(test_client):
    """Test getting total hubfile views."""
    with test_client.application.app_context():
        service = HubfileService()
        initial_views = service.total_hubfile_views()
        assert initial_views >= 0


@pytest.mark.integration
def test_hubfile_total_downloads(test_client):
    """Test getting total hubfile downloads."""
    with test_client.application.app_context():
        service = HubfileService()
        initial_downloads = service.total_hubfile_downloads()
        assert initial_downloads >= 0


@pytest.mark.integration
def test_hubfile_count(test_client):
    """Test counting hubfiles."""
    with test_client.application.app_context():
        service = HubfileService()

        # Get initial count
        initial_count = service.count()

        # Create dependencies
        fm_metadata = FMMetaData(
            uvl_filename="count_test.uvl",
            title="Count Test",
            description="Test",
            publication_type=PublicationType.NONE,
        )
        db.session.add(fm_metadata)
        db.session.commit()

        feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
        db.session.add(feature_model)
        db.session.commit()

        # Create hubfile
        hubfile = service.create(name="count.uvl", checksum="count123", size=512, feature_model_id=feature_model.id)
        assert service.count() == initial_count + 1

        # Cleanup
        service.delete(hubfile.id)
        db.session.delete(feature_model)
        db.session.commit()
        assert service.count() == initial_count


@pytest.mark.integration
def test_hubfile_download_route_not_found(test_client):
    """Test hubfile download route with non-existent file."""
    response = test_client.get("/file/download/99999")
    assert response.status_code in [404, 500]


@pytest.mark.integration
def test_hubfile_view_route_not_found(test_client):
    """Test hubfile view route with non-existent file."""
    response = test_client.get("/file/view/99999")
    assert response.status_code in [404, 500]


@pytest.mark.integration
def test_hubfile_repository_get_by_id(test_client):
    """Test getting hubfile by id through repository."""
    with test_client.application.app_context():
        from app.modules.hubfile.repositories import HubfileRepository

        repo = HubfileRepository()

        # Create dependencies
        fm_metadata = FMMetaData(
            uvl_filename="repo_test.uvl",
            title="Repo Test",
            description="Test",
            publication_type=PublicationType.NONE,
        )
        db.session.add(fm_metadata)
        db.session.commit()

        feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
        db.session.add(feature_model)
        db.session.commit()

        # Create hubfile
        hubfile = Hubfile(name="repo.uvl", checksum="repo123", size=512, feature_model_id=feature_model.id)
        db.session.add(hubfile)
        db.session.commit()

        # Get by id
        retrieved = repo.get_by_id(hubfile.id)
        assert retrieved is not None
        assert retrieved.name == "repo.uvl"

        # Cleanup
        db.session.delete(hubfile)
        db.session.delete(feature_model)
        db.session.commit()


@pytest.mark.integration
def test_hubfile_repository_create(test_client):
    """Test creating hubfile through repository."""
    with test_client.application.app_context():
        from app.modules.hubfile.repositories import HubfileRepository

        repo = HubfileRepository()

        # Create dependencies
        fm_metadata = FMMetaData(
            uvl_filename="create_repo.uvl",
            title="Create Repo",
            description="Test",
            publication_type=PublicationType.NONE,
        )
        db.session.add(fm_metadata)
        db.session.commit()

        feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
        db.session.add(feature_model)
        db.session.commit()

        # Create through repository
        hubfile = repo.create(name="create.uvl", checksum="create123", size=1024, feature_model_id=feature_model.id)
        assert hubfile is not None
        assert hubfile.name == "create.uvl"

        # Cleanup
        db.session.delete(hubfile)
        db.session.delete(feature_model)
        db.session.commit()


@pytest.mark.integration
def test_hubfile_model_attributes(test_client):
    """Test Hubfile model has expected attributes."""
    with test_client.application.app_context():
        # Create dependencies
        fm_metadata = FMMetaData(
            uvl_filename="attr_test.uvl",
            title="Attr Test",
            description="Test",
            publication_type=PublicationType.NONE,
        )
        db.session.add(fm_metadata)
        db.session.commit()

        feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
        db.session.add(feature_model)
        db.session.commit()

        hubfile = Hubfile(name="attr.uvl", checksum="attr123", size=256, feature_model_id=feature_model.id)
        db.session.add(hubfile)
        db.session.commit()

        assert hasattr(hubfile, "id")
        assert hasattr(hubfile, "name")
        assert hasattr(hubfile, "checksum")
        assert hasattr(hubfile, "size")
        assert hasattr(hubfile, "feature_model_id")

        # Cleanup
        db.session.delete(hubfile)
        db.session.delete(feature_model)
        db.session.commit()


@pytest.mark.integration
def test_hubfile_service_get_or_404(test_client):
    """Test HubfileService get_or_404 method."""
    with test_client.application.app_context():
        service = HubfileService()

        # Create dependencies
        fm_metadata = FMMetaData(
            uvl_filename="get404_test.uvl",
            title="Get404 Test",
            description="Test",
            publication_type=PublicationType.NONE,
        )
        db.session.add(fm_metadata)
        db.session.commit()

        feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
        db.session.add(feature_model)
        db.session.commit()

        # Create hubfile
        hubfile = service.create(name="get404.uvl", checksum="get404", size=512, feature_model_id=feature_model.id)

        # Get with valid ID
        retrieved = service.get_or_404(hubfile.id)
        assert retrieved is not None
        assert retrieved.id == hubfile.id

        # Cleanup
        service.delete(hubfile.id)
        db.session.delete(feature_model)
        db.session.commit()


@pytest.mark.integration
def test_hubfile_service_update(test_client):
    """Test updating a hubfile through service."""
    with test_client.application.app_context():
        service = HubfileService()

        # Create dependencies
        fm_metadata = FMMetaData(
            uvl_filename="update_test.uvl",
            title="Update Test",
            description="Test",
            publication_type=PublicationType.NONE,
        )
        db.session.add(fm_metadata)
        db.session.commit()

        feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
        db.session.add(feature_model)
        db.session.commit()

        # Create hubfile
        hubfile = service.create(name="update.uvl", checksum="update123", size=512, feature_model_id=feature_model.id)
        original_id = hubfile.id

        # Update
        updated = service.update(hubfile.id, size=1024)
        assert updated is not None
        assert updated.id == original_id
        assert updated.size == 1024

        # Cleanup
        service.delete(hubfile.id)
        db.session.delete(feature_model)
        db.session.commit()
