from datetime import datetime, timezone

import pytest

from app import create_app, db
from app.modules.auth.models import User
from app.modules.dataset.models import (
    Author,
    DataSource,
    DSDownloadRecord,
    DSMetaData,
    DSViewRecord,
    MaterialRecord,
    MaterialsDataset,
    PublicationType,
)
from app.modules.profile.models import UserProfile


@pytest.fixture(scope="session")
def test_app():
    """Create and configure a new app instance for each test session."""
    test_app = create_app("testing")

    with test_app.app_context():
        # Imprimir los blueprints registrados
        print("TESTING SUITE (1): Blueprints registrados:", test_app.blueprints)
        yield test_app


@pytest.fixture(scope="module")
def test_client(test_app):

    with test_app.test_client() as testing_client:
        with test_app.app_context():
            print("TESTING SUITE (2): Blueprints registrados:", test_app.blueprints)

            # Rollback any pending transactions
            db.session.rollback()
            db.session.remove()

            # Drop all tables with foreign key checks disabled
            with db.engine.begin() as conn:
                conn.execute(db.text("SET FOREIGN_KEY_CHECKS=0"))

                # Get all table names
                result = conn.execute(db.text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = DATABASE()"
                ))
                tables = [row[0] for row in result]

                # Drop each table
                for table in tables:
                    conn.execute(db.text(f"DROP TABLE IF EXISTS `{table}`"))

                conn.execute(db.text("SET FOREIGN_KEY_CHECKS=1"))

            # Recreate all tables
            db.create_all()

            """
            The test suite always includes the following user in order to avoid repetition
            of its creation
            """
            user_test = User(email="test@example.com", password="test1234")
            db.session.add(user_test)
            db.session.commit()

            # Create profile for test user
            profile_test = UserProfile(user_id=user_test.id, name="Test", surname="User")
            db.session.add(profile_test)
            db.session.commit()

            print("Rutas registradas:")
            for rule in test_app.url_map.iter_rules():
                print(rule)
            yield testing_client

            db.session.rollback()
            db.session.remove()

            # Drop all tables with foreign key checks disabled
            with db.engine.begin() as conn:
                conn.execute(db.text("SET FOREIGN_KEY_CHECKS=0"))

                # Get all table names
                result = conn.execute(db.text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE'"
                ))
                tables = [row[0] for row in result]

                # Drop each table
                for table in tables:
                    try:
                        conn.execute(db.text(f"DROP TABLE `{table}`"))
                    except Exception:
                        pass  # Ignore errors

                conn.execute(db.text("SET FOREIGN_KEY_CHECKS=1"))


@pytest.fixture(scope="function")
def clean_database():
    db.session.remove()
    # Disable foreign key checks for MySQL
    db.session.execute(db.text("SET FOREIGN_KEY_CHECKS=0;"))
    db.session.commit()
    db.drop_all()
    db.session.execute(db.text("SET FOREIGN_KEY_CHECKS=1;"))
    db.session.commit()
    db.create_all()
    yield
    db.session.remove()
    # Disable foreign key checks for MySQL
    db.session.execute(db.text("SET FOREIGN_KEY_CHECKS=0;"))
    db.session.commit()
    db.drop_all()
    db.session.execute(db.text("SET FOREIGN_KEY_CHECKS=1;"))
    db.session.commit()
    db.create_all()


@pytest.fixture(scope="function")
def integration_test_data(test_client):
    """Create test data for integration tests."""
    # Rollback any pending transaction first
    db.session.rollback()

    # Delete existing test data if it exists (test_client has module scope)
    # Delete in reverse order of foreign keys - children first, then parents

    # First, delete download and view records (they reference datasets)
    db.session.query(DSDownloadRecord).delete(synchronize_session=False)
    db.session.query(DSViewRecord).delete(synchronize_session=False)

    # Then delete material records (they reference datasets)
    db.session.query(MaterialRecord).delete(synchronize_session=False)

    # Then delete authors (they reference ds_meta_data)
    db.session.query(Author).delete(synchronize_session=False)

    # Now we can delete datasets (they reference ds_meta_data and users)
    db.session.query(MaterialsDataset).delete(synchronize_session=False)

    # Delete metadata
    db.session.query(DSMetaData).delete(synchronize_session=False)

    # Delete user profile and user
    existing_profile = UserProfile.query.filter_by(name="User", surname="One").first()
    if existing_profile:
        db.session.delete(existing_profile)

    existing_user = User.query.filter_by(email="user1@example.com").first()
    if existing_user:
        db.session.delete(existing_user)

    db.session.commit()

    # Crear usuario y perfil
    user1 = User(email="user1@example.com", password="test1234")
    db.session.add(user1)
    db.session.commit()  # Commit to get the ID

    profile1 = UserProfile(user_id=user1.id, name="User", surname="One")
    db.session.add(profile1)
    db.session.commit()  # Commit profile

    # Crear metadatos de datasets
    ds_meta1 = DSMetaData(
        title="Machine Learning Dataset",
        description="A dataset about machine learning patterns",
        publication_type=PublicationType.CONFERENCE_PAPER,
        dataset_doi="10.1234/ml.2024.001",
        tags="machine learning, patterns, software",
    )
    ds_meta2 = DSMetaData(
        title="Software Patterns Dataset",
        description="A dataset about software design patterns",
        publication_type=PublicationType.JOURNAL_ARTICLE,
        dataset_doi="10.1234/patterns.2024.002",
        tags="patterns, design, software",
    )
    ds_meta3 = DSMetaData(
        title="Unsynchronized Dataset",
        description="A dataset without DOI for testing",
        publication_type=PublicationType.WORKING_PAPER,
        dataset_doi=None,
        tags="testing, unsynchronized",
    )
    db.session.add_all([ds_meta1, ds_meta2, ds_meta3])
    db.session.flush()

    # Crear datasets
    dataset1 = MaterialsDataset(user_id=user1.id, ds_meta_data_id=ds_meta1.id, created_at=datetime.now(timezone.utc))
    dataset2 = MaterialsDataset(user_id=user1.id, ds_meta_data_id=ds_meta2.id, created_at=datetime.now(timezone.utc))
    dataset3 = MaterialsDataset(user_id=user1.id, ds_meta_data_id=ds_meta3.id, created_at=datetime.now(timezone.utc))
    db.session.add_all([dataset1, dataset2, dataset3])
    db.session.flush()

    # Crear material records para cada dataset
    material1 = MaterialRecord(
        materials_dataset_id=dataset1.id,
        material_name="Graphene",
        chemical_formula="C",
        structure_type="2D",
        property_name="Thermal Conductivity",
        property_value="5000",
        property_unit="W/mK",
        temperature=300,
        data_source=DataSource.EXPERIMENTAL,
        description="Machine learning model prediction for graphene",
    )
    material2 = MaterialRecord(
        materials_dataset_id=dataset1.id,
        material_name="Silicon",
        chemical_formula="Si",
        structure_type="Crystal",
        property_name="Band Gap",
        property_value="1.12",
        property_unit="eV",
        temperature=300,
        data_source=DataSource.COMPUTATIONAL,
        description="Computational study",
    )
    material3 = MaterialRecord(
        materials_dataset_id=dataset2.id,
        material_name="Steel Alloy",
        chemical_formula="Fe-C",
        structure_type="Metallic",
        property_name="Yield Strength",
        property_value="250",
        property_unit="MPa",
        temperature=298,
        data_source=DataSource.EXPERIMENTAL,
        description="Pattern analysis for steel",
    )
    material4 = MaterialRecord(
        materials_dataset_id=dataset3.id,
        material_name="Test Material",
        chemical_formula="XYZ",
        structure_type="Unknown",
        property_name="Test Property",
        property_value="100",
        property_unit="unit",
        data_source=DataSource.OTHER,
        description="Testing material",
    )
    db.session.add_all([material1, material2, material3, material4])

    # Crear autores
    author1 = Author(name="Jane Smith", affiliation="MIT", ds_meta_data_id=ds_meta1.id)
    author2 = Author(name="John Doe", affiliation="Stanford", ds_meta_data_id=ds_meta1.id)
    # Dataset2 también necesita un autor para aparecer en explore (join con authors)
    author3_ds2 = Author(name="Jane Smith", affiliation="MIT", ds_meta_data_id=ds_meta2.id)
    db.session.add_all([author1, author2, author3_ds2])

    # Crear registros de descarga y visualización
    download_record = DSDownloadRecord(
        user_id=user1.id,
        dataset_id=dataset1.id,
        download_date=datetime.now(timezone.utc),
        download_cookie="test_cookie_123",
    )
    view_record = DSViewRecord(
        user_id=user1.id,
        dataset_id=dataset1.id,
        view_date=datetime.now(timezone.utc),
        view_cookie="test_view_cookie_123",
    )
    db.session.add_all([download_record, view_record])

    # Commit para que los datos estén disponibles
    db.session.commit()

    yield

    # No cleanup needed - test_client fixture handles db.drop_all() at teardown


def login(test_client, email, password):
    """
    Authenticates the user with the credentials provided.

    Args:
        test_client: Flask test client.
        email (str): User's email address.
        password (str): User's password.

    Returns:
        response: POST login request response.
    """
    response = test_client.post("/login", data=dict(email=email, password=password), follow_redirects=True)
    return response


def logout(test_client):
    """
    Logs out the user.

    Args:
        test_client: Flask test client.

    Returns:
        response: Response to GET request to log out.
    """
    return test_client.get("/logout", follow_redirects=True)
