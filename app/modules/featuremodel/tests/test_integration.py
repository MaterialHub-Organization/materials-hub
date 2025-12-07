"""
Integration tests for featuremodel module.
"""

import pytest

from app import db
from app.modules.dataset.models import PublicationType
from app.modules.featuremodel.models import FeatureModel, FMMetaData
from app.modules.featuremodel.services import FeatureModelService


@pytest.mark.integration
def test_featuremodel_service_initialization(test_client):
    """Test FeatureModelService can be initialized."""
    with test_client.application.app_context():
        service = FeatureModelService()
        assert service is not None


@pytest.mark.integration
def test_create_fm_metadata(test_client):
    """Test creating FM metadata."""
    with test_client.application.app_context():
        fm_metadata = FMMetaData(
            uvl_filename="integration_test.uvl",
            title="Integration Test Feature Model",
            description="Test description",
            publication_type=PublicationType.NONE,
        )
        db.session.add(fm_metadata)
        db.session.commit()

        assert fm_metadata.id is not None
        assert fm_metadata.title == "Integration Test Feature Model"

        # Cleanup
        db.session.delete(fm_metadata)
        db.session.commit()


@pytest.mark.integration
def test_create_feature_model(test_client):
    """Test creating a feature model."""
    with test_client.application.app_context():
        # Create metadata first
        fm_metadata = FMMetaData(
            uvl_filename="fm_integration.uvl",
            title="FM Integration",
            description="Test",
            publication_type=PublicationType.NONE,
        )
        db.session.add(fm_metadata)
        db.session.commit()

        # Create feature model
        feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
        db.session.add(feature_model)
        db.session.commit()

        assert feature_model.id is not None
        assert feature_model.fm_meta_data_id == fm_metadata.id

        # Cleanup - cascade delete will remove fm_metadata automatically
        db.session.delete(feature_model)
        db.session.commit()


@pytest.mark.integration
def test_feature_model_relationship(test_client):
    """Test relationship between feature model and metadata."""
    with test_client.application.app_context():
        # Create metadata
        fm_metadata = FMMetaData(
            uvl_filename="relationship_test.uvl",
            title="Relationship Test",
            description="Test",
            publication_type=PublicationType.NONE,
        )
        db.session.add(fm_metadata)
        db.session.commit()

        # Create feature model
        feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
        db.session.add(feature_model)
        db.session.commit()

        # Test relationship
        assert feature_model.fm_meta_data == fm_metadata
        assert feature_model in fm_metadata.feature_model

        # Cleanup - cascade delete will remove fm_metadata automatically
        db.session.delete(feature_model)
        db.session.commit()


@pytest.mark.integration
def test_featuremodel_repository_operations(test_client):
    """Test basic repository operations for feature model."""
    with test_client.application.app_context():
        service = FeatureModelService()

        # Create metadata first
        fm_metadata = FMMetaData(
            uvl_filename="repo_test.uvl",
            title="Repository Test",
            description="Test",
            publication_type=PublicationType.NONE,
        )
        db.session.add(fm_metadata)
        db.session.commit()

        # Create feature model
        created = service.create(fm_meta_data_id=fm_metadata.id)
        assert created.id is not None

        # Get by id
        retrieved = service.get_by_id(created.id)
        assert retrieved is not None

        # Delete - cascade delete will remove fm_metadata automatically
        service.delete(created.id)


@pytest.mark.integration
def test_featuremodel_count(test_client):
    """Test counting feature models."""
    with test_client.application.app_context():
        service = FeatureModelService()

        # Get initial count
        initial_count = service.count()

        # Create metadata first
        fm_metadata = FMMetaData(
            uvl_filename="count_test.uvl",
            title="Count Test",
            description="Test",
            publication_type=PublicationType.NONE,
        )
        db.session.add(fm_metadata)
        db.session.commit()

        # Create feature model
        feature_model = service.create(fm_meta_data_id=fm_metadata.id)
        assert service.count() == initial_count + 1

        # Cleanup
        service.delete(feature_model.id)
        assert service.count() == initial_count

