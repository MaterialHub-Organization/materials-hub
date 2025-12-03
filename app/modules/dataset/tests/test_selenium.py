import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver


# ==============================
# Helpers
# ==============================

def wait_for_page_to_load(driver, timeout=15):
    """Espera a que el DOM esté completamente cargado."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def get_example_csv_path() -> str:
    """
    Devuelve la ruta absoluta al fichero examples/materials_examples.csv
    asumiendo que este test está en app/modules/dataset/tests/test_selenium.py
    y que la estructura del proyecto es:

    project_root/
    ├── app/
    │   └── modules/...
    ├── examples/
    │   └── materials_examples.csv
    """
    root = Path(__file__).resolve().parents[4]
    csv_path = root / "examples" / "materials_example.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"No se encuentra el CSV en {csv_path}")

    return str(csv_path)


def login(driver, host: str, email: str = "user1@example.com", password: str = "1234"):
    """Hace login con el usuario de pruebas."""
    driver.get(f"{host}/login")
    wait_for_page_to_load(driver)

    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    password_field = driver.find_element(By.NAME, "password")

    email_field.send_keys(email)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)

    wait_for_page_to_load(driver)


from selenium.common.exceptions import TimeoutException

def create_materials_dataset_and_go_to_csv_upload(driver, host: str, title_suffix: str = ""):
    """
    Crea un MaterialsDataset usando /dataset/upload y devuelve:

    - dataset_id (str)
    - dataset_title (str)

    Al terminar, el navegador se queda en /materials/<id>/upload.
    """
    driver.get(f"{host}/dataset/upload")
    wait_for_page_to_load(driver)

    dataset_title = f"Selenium Materials Dataset {title_suffix}".strip()

    try:
        # Intentamos encontrar el campo title
        title_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "title"))
        )
    except TimeoutException:
        # 💥 Aquí es donde estás ahora: no aparece el input title
        # Volcamos la URL y el HTML a un fichero para verlo
        html_path = "/tmp/selenium_dataset_upload_error.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        print("\n[DEBUG] No se encontró el input name='title' en /dataset/upload")
        print(f"[DEBUG] URL actual        : {driver.current_url}")
        print(f"[DEBUG] HTML guardado en  : {html_path}\n")
        # Relanzamos la excepción para que el test siga marcando FAILED
        raise

    # Si llegamos aquí, sí existe el campo title
    desc_input = driver.find_element(By.NAME, "desc")
    tags_input = driver.find_element(By.NAME, "tags")

    title_input.send_keys(dataset_title)
    desc_input.send_keys("Dataset de materiales creado automáticamente con Selenium.")
    tags_input.send_keys("selenium,materials,test")

    agree_checkbox = driver.find_element(By.ID, "agreeCheckbox")
    agree_checkbox.click()

    upload_button = driver.find_element(By.ID, "upload_button")
    upload_button.click()

    csv_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "csvFile"))
    )
    wait_for_page_to_load(driver)

    current_url = driver.current_url.rstrip("/")
    parts = current_url.split("/")

    if "materials" not in parts:
        raise AssertionError(f"URL inesperada tras crear dataset: {current_url}")

    idx = parts.index("materials")
    dataset_id = parts[idx + 1]

    return dataset_id, dataset_title


def upload_csv_for_dataset(driver):
    """
    Asume que estamos en /materials/<id>/upload.
    Sube el CSV de ejemplo y comprueba el mensaje de éxito.
    """
    csv_path = get_example_csv_path()
    csv_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "csvFile"))
    )
    csv_input.send_keys(csv_path)

    upload_btn = driver.find_element(By.ID, "uploadBtn")
    upload_btn.click()

    # Esperar a que aparezca el contenedor de resultado
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "uploadResult"))
    )

    # Esperar al texto de éxito
    WebDriverWait(driver, 30).until(
        EC.text_to_be_present_in_element(
            (By.ID, "uploadResult"),
            "CSV uploaded and parsed successfully"
        )
    )


def go_to_view_dataset_from_upload_result(driver, dataset_id: str):
    """Pulsa 'View Dataset' en la página de upload CSV y comprueba la URL."""
    # Usar un selector más flexible para el botón "View Dataset"
    view_dataset_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'View Dataset')] | //button[contains(text(), 'View Dataset')]"))
    )
    view_dataset_link.click()
    wait_for_page_to_load(driver)

    if f"/materials/{dataset_id}" not in driver.current_url:
        raise AssertionError(
            f"No hemos llegado a /materials/{dataset_id}, URL actual: {driver.current_url}"
        )


# ==============================
# Tests
# ==============================

def test_create_materials_dataset_upload_csv_and_view():
    """
    Flujo E2E principal:

    1. Login
    2. Crear Materials Dataset (metadatos)
    3. Subir CSV de ejemplo
    4. Ver el dataset (/materials/<id>)
    5. Abrir el modal de CSV y comprobar que tiene cabeceras y filas
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        # 1) Login
        login(driver, host)

        # 2) Crear dataset y llegar a /materials/<id>/upload
        dataset_id, dataset_title = create_materials_dataset_and_go_to_csv_upload(
            driver, host, title_suffix="E2E"
        )

        # 3) Subir CSV
        upload_csv_for_dataset(driver)

        # 4) Ir a "View Dataset"
        go_to_view_dataset_from_upload_result(driver, dataset_id)

        # 5) Comprobar que hay registros en la vista del dataset
        # Usar selector más específico (id, clase, xpath concreto)
        record_count_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'record-count') or @id='recordCount']"))
        )
        total_from_badge = int(record_count_element.text.strip())

        material_items = driver.find_elements(By.CLASS_NAME, "material-record-item")

        assert total_from_badge >= len(material_items)
        assert total_from_badge > 0, "No se han creado registros a partir del CSV"

        # 6) Abrir modal "View" del CSV con selector más flexible
        view_csv_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@onclick, 'viewCSV') or contains(text(), 'View CSV')]"))
        )
        view_csv_button.click()

        # Esperar a que el modal sea visible (selector flexible)
        modal = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(@class, 'modal') and contains(@id, 'csv')]"))
        )

        # Esperar cabeceras y filas (selectors más específicos)
        headers_cells = WebDriverWait(driver, 15).until(
            lambda d: d.find_elements(By.XPATH, "//table//thead//th | //*[@id='csvHeaders']//th")
        )
        body_rows = driver.find_elements(By.XPATH, "//table//tbody//tr | //*[@id='csvBody']//tr")

        assert headers_cells, "No se han cargado cabeceras en la tabla del CSV"
        assert body_rows, "No se han cargado filas en la tabla del CSV"

    finally:
        close_driver(driver)


def test_dataset_appears_in_my_materials_and_can_be_deleted():
    """
    Flujo:

    1. Login
    2. Crear Materials Dataset + subir CSV
    3. Ir a /dataset/list (My Materials Datasets)
    4. Comprobar que aparece el dataset
    5. Borrarlo usando el prompt 'DELETE'
    6. Comprobar que ya no aparece en la lista
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        # 1) Login
        login(driver, host)

        # 2) Crear dataset y subir CSV
        dataset_id, dataset_title = create_materials_dataset_and_go_to_csv_upload(
            driver, host, title_suffix="ToDelete"
        )
        upload_csv_for_dataset(driver)

        # 3) Ir a la lista de datasets del usuario
        driver.get(f"{host}/dataset/list")
        wait_for_page_to_load(driver)

        # 4) Buscar nuestro dataset en la tabla
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

        assert rows, "No hay filas en la tabla de My Materials Datasets"

        target_row = None
        for row in rows:
            if dataset_title in row.text:
                target_row = row
                break

        assert target_row is not None, f"No se ha encontrado el dataset '{dataset_title}' en la lista"

        # 5) Pulsar el icono de borrar (deleteDataset(...))
        delete_link = target_row.find_element(
            By.XPATH, ".//a[contains(@onclick, 'deleteDataset')]"
        )
        delete_link.click()

        # 6) Gestionar el prompt de JS que pide escribir 'DELETE'
        alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert.send_keys("DELETE")
        alert.accept()

        # 7) Esperar recarga y comprobar que el dataset ya no aparece
        wait_for_page_to_load(driver)
        table2 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        rows_after = table2.find_elements(By.CSS_SELECTOR, "tbody tr")
        text_after = "\n".join(row.text for row in rows_after)
        assert dataset_title not in text_after, "El dataset sigue apareciendo en la lista tras borrarlo"

    finally:
        close_driver(driver)


def test_material_search_filter_works_with_example_csv():
    """
    Flujo extra:

    1. Login
    2. Crear Materials Dataset + subir CSV
    3. Ir a /materials/<id>
    4. Usar el cuadro de búsqueda por nombre de material
       (ej: 'alumina', que viene en el CSV de ejemplo)
    5. Comprobar que se filtran los registros mostrados
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        # 1) Login
        login(driver, host)

        # 2) Crear dataset y subir CSV
        dataset_id, dataset_title = create_materials_dataset_and_go_to_csv_upload(
            driver, host, title_suffix="Search"
        )
        upload_csv_for_dataset(driver)

        # 3) Ir a la vista del dataset
        go_to_view_dataset_from_upload_result(driver, dataset_id)

        # 4) Localizar input de búsqueda (selector más flexible)
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='materialSearchInput' or contains(@placeholder, 'search')]"))
        )
        search_input.clear()
        search_input.send_keys("alumina")

        # Esperar explícitamente a que se filtre (mejor que sleep)
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, ".material-record-item:not([style*='display: none'])")) > 0
        )

        # 5) Comprobar items visibles
        items = driver.find_elements(By.CSS_SELECTOR, ".material-record-item")
        visible_count = 0
        for item in items:
            style = item.get_attribute("style") or ""
            if "display: none" not in style:
                visible_count += 1
                # Usar texto del item en vez de data-attribute si no existe
                item_text = item.text.lower()
                assert "alumina" in item_text, f"Item no contiene 'alumina': {item_text}"

        assert visible_count > 0, "El filtro no ha dejado visible ningún material"

    finally:
        close_driver(driver)
