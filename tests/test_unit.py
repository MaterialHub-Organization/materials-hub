"""
Consolidated unit tests for all modules.
"""
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
from flask import url_for
from wtforms import SubmitField

import docker
from app import db
from app.modules.auth.repositories import UserRepository
from app.modules.auth.services import AuthenticationService
from app.modules.conftest import login, logout
from app.modules.fakenodo.forms import FakenodoForm
from app.modules.fakenodo.models import Deposition
from app.modules.fakenodo.repositories import DepositionRepository
from app.modules.fakenodo.services import FakenodoService
from app.modules.featuremodel.forms import FeaturemodelForm
from app.modules.featuremodel.models import FeatureModel, FMMetaData, FMMetrics
from app.modules.featuremodel.repositories import FeatureModelRepository, FMMetaDataRepository
from app.modules.featuremodel.services import FeatureModelService
from app.modules.flamapy.forms import FlamapyForm
from app.modules.flamapy.models import Flamapy
from app.modules.flamapy.repositories import FlamapyRepository
from app.modules.flamapy.services import FlamapyService
from app.modules.hubfile.forms import HubfileForm
from app.modules.hubfile.models import Hubfile
from app.modules.hubfile.repositories import HubfileRepository
from app.modules.hubfile.services import HubfileService
from app.modules.profile.repositories import UserProfileRepository
from app.modules.webhook.forms import WebhookForm
from app.modules.webhook.models import Webhook
from app.modules.webhook.repositories import WebhookRepository
from app.modules.webhook.services import WebhookService
from app.modules.zenodo.forms import ZenodoForm
from app.modules.zenodo.models import Zenodo
from app.modules.zenodo.repositories import ZenodoRepository
from app.modules.zenodo.services import ZenodoService

"""
Consolidated unit tests for all modules.
"""


# Common imports for all tests
# ============================================================================
# Tests from app/modules/profile/tests/test_unit.py
# ============================================================================
@pytest.mark.unit
def test_edit_profile_page_get(test_client):
    """
    Tests access to the profile editing page via a GET request.
    """
    login_response = login(test_client, "test@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/profile/edit")
    assert response.status_code == 200, "The profile editing page could not be accessed."
    assert b"Edit profile" in response.data, "The expected content is not present on the page"

    logout(test_client)


# ============================================================================
# Tests from app/modules/auth/tests/test_unit.py
# ============================================================================


@pytest.mark.unit
def test_login_success(test_client):
    response = test_client.post(
        "/login", data=dict(email="test@example.com", password="test1234"), follow_redirects=True
    )

    assert response.request.path != url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


@pytest.mark.unit
def test_login_unsuccessful_bad_email(test_client):
    response = test_client.post(
        "/login", data=dict(email="bademail@example.com", password="test1234"), follow_redirects=True
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


@pytest.mark.unit
def test_login_unsuccessful_bad_password(test_client):
    response = test_client.post(
        "/login", data=dict(email="test@example.com", password="basspassword"), follow_redirects=True
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


@pytest.mark.unit
def test_signup_user_no_name(test_client):
    response = test_client.post(
        "/signup", data=dict(surname="Foo", email="test@example.com", password="test1234"), follow_redirects=True
    )
    assert response.request.path == url_for("auth.show_signup_form"), "Signup was unsuccessful"
    assert b"This field is required" in response.data, response.data


@pytest.mark.unit
def test_signup_user_unsuccessful(test_client):
    email = "test@example.com"
    response = test_client.post(
        "/signup", data=dict(name="Test", surname="Foo", email=email, password="test1234"), follow_redirects=True
    )
    assert response.request.path == url_for("auth.show_signup_form"), "Signup was unsuccessful"
    assert f"Email {email} in use".encode("utf-8") in response.data


@pytest.mark.unit
def test_signup_user_successful(test_client):
    response = test_client.post(
        "/signup",
        data=dict(name="Foo", surname="Example", email="foo@example.com", password="foo1234"),
        follow_redirects=True,
    )
    assert response.request.path == url_for("public.index"), "Signup was unsuccessful"


@pytest.mark.unit
def test_service_create_with_profie_success(clean_database):
    data = {"name": "Test", "surname": "Foo", "email": "service_test@example.com", "password": "test1234"}

    AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 1
    assert UserProfileRepository().count() == 1


@pytest.mark.unit
def test_service_create_with_profile_fail_no_email(clean_database):
    data = {"name": "Test", "surname": "Foo", "email": "", "password": "1234"}

    with pytest.raises(ValueError, match="Email is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


@pytest.mark.unit
def test_service_create_with_profile_fail_no_password(clean_database):
    data = {"name": "Test", "surname": "Foo", "email": "test@example.com", "password": ""}

    with pytest.raises(ValueError, match="Password is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


# ============================================================================
# Tests from app/modules/public/tests/test_unit.py
# ============================================================================


@pytest.mark.unit
def test_index_page_loads(test_client):
    """
    Test that the index page loads successfully and returns 200 status code.
    """
    with patch("app.modules.public.routes.DataSetService") as mock_dataset_service, patch(
        "app.modules.public.routes.FeatureModelService"
    ) as mock_fm_service, patch("app.modules.public.routes.MaterialsDatasetRepository") as mock_materials_repo:
        # Mock service methods
        mock_dataset_service_instance = Mock()
        mock_dataset_service_instance.count_synchronized_datasets.return_value = 10
        mock_dataset_service_instance.total_dataset_downloads.return_value = 100
        mock_dataset_service_instance.total_dataset_views.return_value = 500
        mock_dataset_service_instance.latest_synchronized.return_value = []
        mock_dataset_service.return_value = mock_dataset_service_instance

        mock_fm_service_instance = Mock()
        mock_fm_service_instance.count_feature_models.return_value = 5
        mock_fm_service_instance.total_feature_model_downloads.return_value = 50
        mock_fm_service_instance.total_feature_model_views.return_value = 250
        mock_fm_service.return_value = mock_fm_service_instance

        mock_materials_repo_instance = Mock()
        mock_materials_repo_instance.count_all.return_value = 3
        mock_materials_repo_instance.get_all.return_value = []
        mock_materials_repo.return_value = mock_materials_repo_instance

        response = test_client.get("/")

        assert response.status_code == 200, "The index page should return status code 200"


@pytest.mark.unit
def test_index_page_calls_services(test_client):
    """
    Test that the index page calls all required services.
    """
    with patch("app.modules.public.routes.DataSetService") as mock_dataset_service, patch(
        "app.modules.public.routes.FeatureModelService"
    ) as mock_fm_service, patch("app.modules.public.routes.MaterialsDatasetRepository") as mock_materials_repo:
        # Mock service methods
        mock_dataset_service_instance = Mock()
        mock_dataset_service_instance.count_synchronized_datasets.return_value = 10
        mock_dataset_service_instance.total_dataset_downloads.return_value = 100
        mock_dataset_service_instance.total_dataset_views.return_value = 500
        mock_dataset_service_instance.latest_synchronized.return_value = []
        mock_dataset_service.return_value = mock_dataset_service_instance

        mock_fm_service_instance = Mock()
        mock_fm_service_instance.count_feature_models.return_value = 5
        mock_fm_service_instance.total_feature_model_downloads.return_value = 50
        mock_fm_service_instance.total_feature_model_views.return_value = 250
        mock_fm_service.return_value = mock_fm_service_instance

        mock_materials_repo_instance = Mock()
        mock_materials_repo_instance.count_all.return_value = 3
        mock_materials_repo_instance.get_all.return_value = []
        mock_materials_repo.return_value = mock_materials_repo_instance

        test_client.get("/")

        # Verify service methods were called
        mock_dataset_service_instance.count_synchronized_datasets.assert_called_once()
        mock_dataset_service_instance.total_dataset_downloads.assert_called_once()
        mock_dataset_service_instance.total_dataset_views.assert_called_once()
        mock_dataset_service_instance.latest_synchronized.assert_called_once()
        mock_fm_service_instance.count_feature_models.assert_called_once()
        mock_fm_service_instance.total_feature_model_downloads.assert_called_once()
        mock_fm_service_instance.total_feature_model_views.assert_called_once()
        mock_materials_repo_instance.count_all.assert_called_once()
        mock_materials_repo_instance.get_all.assert_called_once()


# ============================================================================
# Tests from app/modules/hubfile/tests/test_unit.py
# ============================================================================


@pytest.mark.unit
def test_hubfile_repository_initialization():
    """
    Test that HubfileRepository initializes correctly.
    """
    repository = HubfileRepository()
    assert repository is not None
    assert repository.model == Hubfile


@pytest.mark.unit
def test_hubfile_service_initialization():
    """
    Test that HubfileService initializes correctly.
    """
    service = HubfileService()
    assert service is not None
    assert isinstance(service.repository, HubfileRepository)


@pytest.mark.unit
def test_hubfile_get_formatted_size():
    """
    Test Hubfile get_formatted_size method.
    """
    with patch("app.modules.dataset.services.SizeService") as mock_size_service:
        mock_service_instance = Mock()
        mock_service_instance.get_human_readable_size.return_value = "1.5 MB"
        mock_size_service.return_value = mock_service_instance

        hubfile = Hubfile(name="test.uvl", checksum="abc123", size=1500000, feature_model_id=1)
        formatted_size = hubfile.get_formatted_size()

        assert formatted_size == "1.5 MB"
        mock_service_instance.get_human_readable_size.assert_called_once_with(1500000)


@pytest.mark.unit
def test_hubfile_to_dict(test_client):
    """
    Test Hubfile to_dict method.
    """
    with test_client.application.test_request_context():
        hubfile = Hubfile(id=1, name="test.uvl", checksum="abc123", size=1500, feature_model_id=1)

        with patch.object(Hubfile, "get_formatted_size", return_value="1.5 KB"):
            result = hubfile.to_dict()

            assert result["id"] == 1
            assert result["name"] == "test.uvl"
            assert result["checksum"] == "abc123"
            assert result["size_in_bytes"] == 1500
            assert result["size_in_human_format"] == "1.5 KB"
            assert "url" in result


@pytest.mark.unit
def test_hubfile_service_get_path_by_hubfile():
    """
    Test HubfileService get_path_by_hubfile method.
    """
    with patch.dict("os.environ", {"WORKING_DIR": "/app"}):
        service = HubfileService()

        mock_user = Mock()
        mock_user.id = 123

        mock_dataset = Mock()
        mock_dataset.id = 456

        mock_hubfile = Mock()
        mock_hubfile.name = "test.uvl"

        with patch.object(service, "get_owner_user_by_hubfile", return_value=mock_user), patch.object(
            service, "get_dataset_by_hubfile", return_value=mock_dataset
        ):
            path = service.get_path_by_hubfile(mock_hubfile)

            assert path == "/app/uploads/user_123/dataset_456/test.uvl"


@pytest.mark.unit
def test_hubfile_service_total_views():
    """
    Test HubfileService total_hubfile_views method.
    """
    service = HubfileService()

    with patch.object(service.hubfile_view_record_repository, "total_hubfile_views", return_value=250):
        total_views = service.total_hubfile_views()

        assert total_views == 250


@pytest.mark.unit
def test_hubfile_service_total_downloads(test_client):
    """
    Test HubfileService total_hubfile_downloads method.
    """
    with test_client.application.app_context():
        service = HubfileService()

        # Mock the HubfileDownloadRecordRepository class
        with patch("app.modules.hubfile.services.HubfileDownloadRecordRepository") as mock_repo_class:
            mock_repo_instance = Mock()
            mock_repo_instance.total_hubfile_downloads.return_value = 150
            mock_repo_class.return_value = mock_repo_instance

            total_downloads = service.total_hubfile_downloads()

            assert total_downloads == 150
            mock_repo_class.assert_called_once()
            mock_repo_instance.total_hubfile_downloads.assert_called_once()


@pytest.mark.unit
def test_hubfile_form_initialization(test_client):
    """
    Test that HubfileForm initializes correctly.
    """

    with test_client.application.app_context():
        form = HubfileForm()

        assert form is not None
        assert hasattr(form, "submit")
        assert isinstance(form.submit, SubmitField)
        assert form.submit.label.text == "Save hubfile"


# ============================================================================
# Tests from app/modules/flamapy/tests/test_unit.py
# ============================================================================


@pytest.mark.unit
def test_flamapy_model_creation(test_client):
    """
    Test that Flamapy model can be created and saved to database.
    """
    with test_client.application.app_context():
        flamapy = Flamapy()
        db.session.add(flamapy)
        db.session.commit()

        assert flamapy.id is not None, "Flamapy model should have an ID after commit"

        # Cleanup
        db.session.delete(flamapy)
        db.session.commit()


@pytest.mark.unit
def test_flamapy_model_repr(test_client):
    """
    Test that Flamapy model has proper representation.
    """
    with test_client.application.app_context():
        flamapy = Flamapy()
        db.session.add(flamapy)
        db.session.commit()

        representation = repr(flamapy)
        assert "Flamapy" in representation or str(flamapy.id) in representation

        # Cleanup
        db.session.delete(flamapy)
        db.session.commit()


@pytest.mark.unit
def test_valid_endpoint(test_client):
    """
    Test the /flamapy/valid endpoint returns success.
    """
    response = test_client.get("/flamapy/valid/1")

    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["file_id"] == 1


@pytest.mark.unit
def test_check_uvl_endpoint_not_found(test_client):
    """
    Test the /flamapy/check_uvl endpoint with non-existent file.
    """
    with patch("app.modules.flamapy.routes.HubfileService") as mock_service:
        mock_service_instance = Mock()
        mock_service_instance.get_by_id.return_value = None
        mock_service.return_value = mock_service_instance

        response = test_client.get("/flamapy/check_uvl/9999")

        # Should handle the error gracefully
        assert response.status_code in [400, 500]


@pytest.mark.unit
def test_check_uvl_endpoint_with_valid_file(test_client):
    """
    Test the /flamapy/check_uvl endpoint with valid UVL file (mocked).
    """
    with patch("app.modules.flamapy.routes.HubfileService") as mock_hubfile_service, patch(
        "app.modules.flamapy.routes.FileStream"
    ) as _mock_file_stream,  # noqa: F841 patch("app.modules.flamapy.routes.UVLCustomLexer") as mock_lexer, patch(
        "app.modules.flamapy.routes.UVLPythonParser"
    ) as mock_parser, patch(
        "app.modules.flamapy.routes.CommonTokenStream"
    ) as _mock_token_stream:  # noqa: F841
        # Mock hubfile
        mock_hubfile = Mock()
        mock_hubfile.get_path.return_value = "/fake/path.uvl"

        mock_service_instance = Mock()
        mock_service_instance.get_by_id.return_value = mock_hubfile
        mock_hubfile_service.return_value = mock_service_instance

        # Mock lexer and parser with no errors
        mock_lexer_instance = Mock()
        mock_lexer_instance.removeErrorListeners = Mock()
        mock_lexer_instance.addErrorListener = Mock()
        mock_lexer.return_value = mock_lexer_instance

        mock_parser_instance = Mock()
        mock_parser_instance.removeErrorListeners = Mock()
        mock_parser_instance.addErrorListener = Mock()
        mock_parser.return_value = mock_parser_instance

        response = test_client.get("/flamapy/check_uvl/1")

        assert response.status_code == 200
        assert response.json["message"] == "Valid Model"


@pytest.mark.unit
def test_flamapy_repository_initialization():
    """
    Test that FlamapyRepository initializes correctly.
    """

    repository = FlamapyRepository()
    assert repository is not None
    assert repository.model == Flamapy


@pytest.mark.unit
def test_flamapy_service_initialization():
    """
    Test that FlamapyService initializes correctly.
    """

    service = FlamapyService()
    assert service is not None
    assert isinstance(service.repository, FlamapyRepository)


@pytest.mark.unit
def test_flamapy_form_initialization(test_client):
    """
    Test that FlamapyForm initializes correctly.
    """

    with test_client.application.app_context():
        form = FlamapyForm()

        assert form is not None
        assert hasattr(form, "submit")
        assert isinstance(form.submit, SubmitField)
        assert form.submit.label.text == "Save flamapy"


# ============================================================================
# Tests from app/modules/featuremodel/tests/test_unit.py
# ============================================================================


@pytest.mark.unit
def test_feature_model_repository_initialization():
    """
    Test that FeatureModelRepository initializes correctly.
    """
    repository = FeatureModelRepository()
    assert repository is not None
    assert repository.model == FeatureModel


@pytest.mark.unit
def test_fm_metadata_repository_initialization():
    """
    Test that FMMetaDataRepository initializes correctly.
    """
    repository = FMMetaDataRepository()
    assert repository is not None
    assert repository.model == FMMetaData


@pytest.mark.unit
def test_feature_model_service_initialization():
    """
    Test that FeatureModelService initializes correctly.
    """
    service = FeatureModelService()
    assert service is not None
    assert isinstance(service.repository, FeatureModelRepository)


@pytest.mark.unit
def test_feature_model_service_count_feature_models(test_client):
    """
    Test count_feature_models method returns correct count.
    """
    with test_client.application.app_context():
        service = FeatureModelService()
        count = service.count_feature_models()
        assert isinstance(count, int)
        assert count >= 0


@pytest.mark.unit
def test_feature_model_service_total_views(test_client):
    """
    Test total_feature_model_views method.
    """
    with patch("app.modules.featuremodel.services.HubfileService") as mock_hubfile_service:
        mock_service_instance = Mock()
        mock_service_instance.total_hubfile_views.return_value = 100
        mock_hubfile_service.return_value = mock_service_instance

        service = FeatureModelService()
        total_views = service.total_feature_model_views()

        assert total_views == 100
        mock_service_instance.total_hubfile_views.assert_called_once()


@pytest.mark.unit
def test_feature_model_service_total_downloads(test_client):
    """
    Test total_feature_model_downloads method.
    """
    with patch("app.modules.featuremodel.services.HubfileService") as mock_hubfile_service:
        mock_service_instance = Mock()
        mock_service_instance.total_hubfile_downloads.return_value = 50
        mock_hubfile_service.return_value = mock_service_instance

        service = FeatureModelService()
        total_downloads = service.total_feature_model_downloads()

        assert total_downloads == 50
        mock_service_instance.total_hubfile_downloads.assert_called_once()


@pytest.mark.unit
def test_fm_metrics_model_repr(test_client):
    """
    Test FMMetrics model representation.
    """
    with test_client.application.app_context():
        metrics = FMMetrics(solver="SAT Solver", not_solver="None")
        db.session.add(metrics)
        db.session.commit()

        representation = repr(metrics)
        assert "FMMetrics" in representation
        assert "SAT Solver" in representation

        # Cleanup
        db.session.delete(metrics)
        db.session.commit()


@pytest.mark.unit
def test_featuremodel_form_initialization(test_client):
    """
    Test that FeaturemodelForm initializes correctly.
    """

    with test_client.application.app_context():
        form = FeaturemodelForm()

        assert form is not None
        assert hasattr(form, "submit")
        assert isinstance(form.submit, SubmitField)
        assert form.submit.label.text == "Save featuremodel"


# ============================================================================
# Tests from app/modules/webhook/tests/test_unit.py
# ============================================================================


@pytest.mark.unit
def test_webhook_model_creation(test_client):
    """
    Test that Webhook model can be created and saved to database.
    """
    with test_client.application.app_context():
        webhook = Webhook()
        db.session.add(webhook)
        db.session.commit()

        assert webhook.id is not None, "Webhook model should have an ID after commit"

        # Cleanup
        db.session.delete(webhook)
        db.session.commit()


@pytest.mark.unit
def test_webhook_repository_initialization():
    """
    Test that WebhookRepository initializes correctly.
    """
    repository = WebhookRepository()
    assert repository is not None
    assert repository.model == Webhook


@pytest.mark.unit
def test_webhook_service_initialization():
    """
    Test that WebhookService initializes correctly.
    """
    service = WebhookService()
    assert service is not None
    assert isinstance(service.repository, WebhookRepository)


@pytest.mark.unit
def test_webhook_service_get_volume_name():
    """
    Test WebhookService get_volume_name method.
    """
    service = WebhookService()
    mock_container = Mock()
    mock_container.attrs = {"Mounts": [{"Destination": "/app", "Name": "test_volume"}]}

    volume_name = service.get_volume_name(mock_container)
    assert volume_name == "test_volume"


@pytest.mark.unit
def test_webhook_service_get_volume_name_with_source():
    """
    Test WebhookService get_volume_name method with Source instead of Name.
    """
    service = WebhookService()
    mock_container = Mock()
    mock_container.attrs = {"Mounts": [{"Destination": "/app", "Source": "/host/path"}]}

    volume_name = service.get_volume_name(mock_container)
    assert volume_name == "/host/path"


@pytest.mark.unit
def test_webhook_service_get_volume_name_not_found():
    """
    Test WebhookService get_volume_name method when volume not found.
    """
    service = WebhookService()
    mock_container = Mock()
    mock_container.attrs = {"Mounts": [{"Destination": "/other", "Name": "other_volume"}]}

    with pytest.raises(ValueError, match="No volume or bind mount found mounted on /app"):
        service.get_volume_name(mock_container)


@pytest.mark.unit
def test_webhook_form_initialization(test_client):
    """
    Test that WebhookForm initializes correctly.
    """

    with test_client.application.app_context():
        form = WebhookForm()

        assert form is not None
        assert hasattr(form, "submit")
        assert isinstance(form.submit, SubmitField)


@pytest.mark.unit
def test_webhook_service_get_web_container_not_found():
    """
    Test WebhookService get_web_container when container not found.
    """
    service = WebhookService()

    with patch("app.modules.webhook.services.client.containers.get") as mock_get:
        mock_get.side_effect = docker.errors.NotFound("Container not found")

        with pytest.raises(Exception):  # abort raises an exception
            service.get_web_container()


@pytest.mark.unit
def test_webhook_service_execute_container_command_success():
    """
    Test WebhookService execute_container_command with successful command.
    """
    service = WebhookService()
    mock_container = Mock()
    mock_container.exec_run.return_value = (0, b"Command output")

    result = service.execute_container_command(mock_container, "echo test")

    assert result == "Command output"
    mock_container.exec_run.assert_called_once_with("echo test", workdir="/app")


@pytest.mark.unit
def test_webhook_service_execute_container_command_failure():
    """
    Test WebhookService execute_container_command with failed command.
    """
    service = WebhookService()
    mock_container = Mock()
    mock_container.exec_run.return_value = (1, b"Error message")

    with pytest.raises(Exception):  # abort raises an exception
        service.execute_container_command(mock_container, "false")


@pytest.mark.unit
def test_webhook_service_log_deployment():
    """
    Test WebhookService log_deployment method.
    """
    service = WebhookService()
    mock_container = Mock()
    mock_container.exec_run.return_value = (0, b"")

    with patch("app.modules.webhook.services.datetime") as mock_datetime:
        fixed_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed_time

        service.log_deployment(mock_container)

        mock_container.exec_run.assert_called_once()
        call_args = mock_container.exec_run.call_args[0][0]
        assert "Deployment successful" in call_args
        assert "/app/deployments.log" in call_args


@pytest.mark.unit
def test_webhook_service_restart_container():
    """
    Test WebhookService restart_container method.
    """
    service = WebhookService()
    mock_container = Mock()
    mock_container.id = "container_123"

    with patch("app.modules.webhook.services.subprocess.Popen") as mock_popen:
        service.restart_container(mock_container)

        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        assert call_args[0] == "/bin/sh"
        assert "/app/scripts/restart_container.sh" in call_args
        assert "container_123" in call_args


# ============================================================================
# Tests from app/modules/fakenodo/tests/test_unit.py
# ============================================================================


@pytest.mark.unit
def test_deposition_model_creation(test_client):
    """
    Test that Deposition model can be created and saved to database.
    """
    with test_client.application.app_context():
        deposition = Deposition(dep_metadata={"title": "Test"}, status="draft")
        db.session.add(deposition)
        db.session.commit()

        assert deposition.id is not None, "Deposition should have an ID after commit"
        assert deposition.status == "draft"
        assert deposition.dep_metadata["title"] == "Test"

        # Cleanup
        db.session.delete(deposition)
        db.session.commit()


@pytest.mark.unit
def test_deposition_model_repr(test_client):
    """
    Test that Deposition model has proper representation.
    """
    with test_client.application.app_context():
        deposition = Deposition(dep_metadata={"title": "Test"}, status="draft")
        db.session.add(deposition)
        db.session.commit()

        representation = repr(deposition)
        assert "Deposition" in representation
        assert str(deposition.id) in representation

        # Cleanup
        db.session.delete(deposition)
        db.session.commit()


@pytest.mark.unit
def test_deposition_repository_initialization():
    """
    Test that DepositionRepository initializes correctly.
    """
    repository = DepositionRepository()
    assert repository is not None
    assert repository.model == Deposition


@pytest.mark.unit
def test_deposition_repository_create_new_deposition(test_client):
    """
    Test DepositionRepository create_new_deposition method.
    """
    with test_client.application.app_context():
        repository = DepositionRepository()
        metadata = {"title": "Test Deposition", "description": "A test"}

        deposition = repository.create_new_deposition(dep_metadata=metadata)

        assert deposition is not None
        assert deposition.id is not None
        assert deposition.dep_metadata == metadata
        assert deposition.status == "draft"

        # Cleanup
        db.session.delete(deposition)
        db.session.commit()


@pytest.mark.unit
def test_fakenodo_service_initialization():
    """
    Test that FakenodoService initializes correctly.
    """
    service = FakenodoService()
    assert service is not None
    assert isinstance(service.deposition_repository, DepositionRepository)


@pytest.mark.unit
def test_fakenodo_service_create_new_deposition(test_client):
    """
    Test FakenodoService create_new_deposition method.
    """
    with test_client.application.app_context():
        service = FakenodoService()

        # Mock dataset
        mock_dataset = Mock()
        mock_dataset.ds_meta_data.title = "Test Dataset"
        mock_dataset.ds_meta_data.description = "Test Description"
        mock_dataset.ds_meta_data.publication_type.value = "none"
        mock_dataset.ds_meta_data.tags = "tag1, tag2"
        mock_dataset.ds_meta_data.authors = []

        result = service.create_new_deposition(mock_dataset)

        assert result is not None
        assert "id" in result
        assert "metadata" in result
        assert "message" in result
        assert result["metadata"]["title"] == "Test Dataset"

        # Cleanup - delete the created deposition
        deposition_id = result["id"]
        deposition = Deposition.query.get(deposition_id)
        if deposition:
            db.session.delete(deposition)
            db.session.commit()


@pytest.mark.unit
def test_fakenodo_service_publish_deposition(test_client):
    """
    Test FakenodoService publish_deposition method.
    """
    with test_client.application.app_context():
        # Create a test deposition first
        deposition = Deposition(dep_metadata={"title": "Test"}, status="draft")
        db.session.add(deposition)
        db.session.commit()

        service = FakenodoService()
        result = service.publish_deposition(deposition.id)

        assert result is not None
        assert result["id"] == deposition.id
        assert result["status"] == "published"
        assert "conceptdoi" in result
        assert f"10.5281/fakenodo.{deposition.id}" == result["conceptdoi"]

        # Verify deposition was updated
        updated_deposition = Deposition.query.get(deposition.id)
        assert updated_deposition.status == "published"
        assert updated_deposition.doi == f"10.5281/fakenodo.{deposition.id}"

        # Cleanup
        db.session.delete(updated_deposition)
        db.session.commit()


@pytest.mark.unit
def test_fakenodo_service_get_deposition(test_client):
    """
    Test FakenodoService get_deposition method.
    """
    with test_client.application.app_context():
        # Create a test deposition
        metadata = {"title": "Test Deposition"}
        deposition = Deposition(dep_metadata=metadata, status="draft", doi="10.5281/fakenodo.123")
        db.session.add(deposition)
        db.session.commit()

        service = FakenodoService()
        result = service.get_deposition(deposition.id)

        assert result is not None
        assert result["id"] == deposition.id
        assert result["doi"] == "10.5281/fakenodo.123"
        assert result["metadata"] == metadata
        assert result["status"] == "draft"

        # Cleanup
        db.session.delete(deposition)
        db.session.commit()


@pytest.mark.unit
def test_fakenodo_service_get_doi(test_client):
    """
    Test FakenodoService get_doi method.
    """
    with test_client.application.app_context():
        # Create a test deposition with DOI
        deposition = Deposition(dep_metadata={"title": "Test"}, status="published", doi="10.5281/fakenodo.999")
        db.session.add(deposition)
        db.session.commit()

        service = FakenodoService()
        doi = service.get_doi(deposition.id)

        assert doi == "10.5281/fakenodo.999"

        # Cleanup
        db.session.delete(deposition)
        db.session.commit()


@pytest.mark.unit
def test_fakenodo_form_initialization(test_client):
    """
    Test that FakenodoForm initializes correctly.
    """

    with test_client.application.app_context():
        form = FakenodoForm()

        assert form is not None
        assert hasattr(form, "submit")
        assert isinstance(form.submit, SubmitField)
        assert form.submit.label.text == "Save fakenodo"


# ============================================================================
# Tests from app/modules/team/tests/test_unit.py
# ============================================================================


@pytest.mark.unit
def test_team_page_loads(test_client):
    """
    Test that the team page loads successfully and returns 200 status code.
    """
    response = test_client.get("/team")

    assert response.status_code == 200, "The team page should return status code 200"


@pytest.mark.unit
def test_team_page_content(test_client):
    """
    Test that the team page contains expected content.
    """
    response = test_client.get("/team")

    assert response.status_code == 200
    assert b"text/html" in response.content_type.encode(), "Response should be HTML"


# ============================================================================
# Tests from app/modules/zenodo/tests/test_unit.py
# ============================================================================


@pytest.mark.unit
def test_zenodo_model_creation(test_client):
    """
    Test that Zenodo model can be created and saved to database.
    """
    with test_client.application.app_context():
        zenodo = Zenodo()
        db.session.add(zenodo)
        db.session.commit()

        assert zenodo.id is not None, "Zenodo model should have an ID after commit"

        # Cleanup
        db.session.delete(zenodo)
        db.session.commit()


@pytest.mark.unit
def test_zenodo_repository_initialization():
    """
    Test that ZenodoRepository initializes correctly.
    """
    repository = ZenodoRepository()
    assert repository is not None
    assert repository.model == Zenodo


@pytest.mark.unit
def test_zenodo_service_initialization():
    """
    Test that ZenodoService initializes correctly.
    """
    with patch.dict("os.environ", {"ZENODO_ACCESS_TOKEN": "test_token"}):
        service = ZenodoService()
        assert service is not None
        assert isinstance(service.repository, ZenodoRepository)
        assert service.ZENODO_ACCESS_TOKEN == "test_token"
        assert service.headers == {"Content-Type": "application/json"}
        assert service.params == {"access_token": "test_token"}


@pytest.mark.unit
def test_zenodo_service_get_zenodo_url_development():
    """
    Test that get_zenodo_url returns correct URL for development environment.
    """
    with patch.dict(
        "os.environ",
        {"FLASK_ENV": "development", "ZENODO_API_URL": "https://sandbox.zenodo.org/api/deposit/depositions"},
    ):
        service = ZenodoService()
        url = service.get_zenodo_url()
        assert url == "https://sandbox.zenodo.org/api/deposit/depositions"


@pytest.mark.unit
def test_zenodo_service_get_zenodo_url_production():
    """
    Test that get_zenodo_url returns correct URL for production environment.
    """
    with patch.dict(
        "os.environ", {"FLASK_ENV": "production", "ZENODO_API_URL": "https://zenodo.org/api/deposit/depositions"}
    ):
        service = ZenodoService()
        url = service.get_zenodo_url()
        assert url == "https://zenodo.org/api/deposit/depositions"


@pytest.mark.unit
def test_zenodo_service_get_zenodo_access_token():
    """
    Test that get_zenodo_access_token returns correct token.
    """
    with patch.dict("os.environ", {"ZENODO_ACCESS_TOKEN": "my_secret_token"}):
        service = ZenodoService()
        token = service.get_zenodo_access_token()
        assert token == "my_secret_token"


@pytest.mark.unit
def test_zenodo_service_test_connection_success():
    """
    Test successful connection test to Zenodo.
    """
    with patch.dict("os.environ", {"ZENODO_ACCESS_TOKEN": "test_token"}):
        service = ZenodoService()

        with patch("app.modules.zenodo.services.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            result = service.test_connection()

            assert result is True
            mock_get.assert_called_once()


@pytest.mark.unit
def test_zenodo_service_test_connection_failure():
    """
    Test failed connection test to Zenodo.
    """
    with patch.dict("os.environ", {"ZENODO_ACCESS_TOKEN": "test_token"}):
        service = ZenodoService()

        with patch("app.modules.zenodo.services.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_get.return_value = mock_response

            result = service.test_connection()

            assert result is False


@pytest.mark.unit
def test_zenodo_service_get_all_depositions():
    """
    Test get_all_depositions method.
    """
    with patch.dict("os.environ", {"ZENODO_ACCESS_TOKEN": "test_token"}):
        service = ZenodoService()

        with patch("app.modules.zenodo.services.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"id": 1, "title": "Test Deposition"}]
            mock_get.return_value = mock_response

            result = service.get_all_depositions()

            assert result == [{"id": 1, "title": "Test Deposition"}]
            mock_get.assert_called_once()


@pytest.mark.unit
def test_zenodo_service_get_deposition():
    """
    Test get_deposition method.
    """
    with patch.dict("os.environ", {"ZENODO_ACCESS_TOKEN": "test_token"}):
        service = ZenodoService()

        with patch("app.modules.zenodo.services.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": 123, "doi": "10.5281/zenodo.123"}
            mock_get.return_value = mock_response

            result = service.get_deposition(123)

            assert result["id"] == 123
            assert result["doi"] == "10.5281/zenodo.123"


@pytest.mark.unit
def test_zenodo_service_get_doi():
    """
    Test get_doi method.
    """
    with patch.dict("os.environ", {"ZENODO_ACCESS_TOKEN": "test_token"}):
        service = ZenodoService()

        with patch.object(service, "get_deposition", return_value={"doi": "10.5281/zenodo.456"}):
            doi = service.get_doi(456)

            assert doi == "10.5281/zenodo.456"


@pytest.mark.unit
def test_zenodo_form_initialization(test_client):
    """
    Test that ZenodoForm initializes correctly.
    """

    with test_client.application.app_context():
        form = ZenodoForm()

        assert form is not None
        assert hasattr(form, "submit")
        assert isinstance(form.submit, SubmitField)
        assert form.submit.label.text == "Save zenodo"
