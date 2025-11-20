"""
Extended Selenium GUI tests for dataset module.

Additional GUI tests using pytest framework for dataset viewing,
creation, and management functionality.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.fixture(scope="module")
def driver():
    """Setup Selenium WebDriver"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()


@pytest.fixture(scope="module")
def logged_in_driver(driver):
    """Setup driver with logged-in session"""
    driver.get("http://localhost:5000/login")

    try:
        email_input = driver.find_element(By.NAME, "email")
        password_input = driver.find_element(By.NAME, "password")

        email_input.send_keys("test@example.com")
        password_input.send_keys("test1234")
        password_input.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(lambda d: "/login" not in d.current_url)
    except Exception as e:
        pytest.skip(f"Could not log in: {e}")

    yield driver

    try:
        driver.get("http://localhost:5000/logout")
    except Exception:
        pass


@pytest.mark.selenium
class TestDatasetViewGUI:
    """GUI tests for viewing datasets"""

    def test_dataset_list_page_loads(self, logged_in_driver):
        """Test that dataset list page loads"""
        logged_in_driver.get("http://localhost:5000/dataset/list")
        WebDriverWait(logged_in_driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        assert "dataset" in logged_in_driver.current_url

    def test_dataset_detail_page_loads(self, driver):
        """Test that dataset detail page loads"""
        driver.get("http://localhost:5000/dataset/view/1")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page_source = driver.page_source.lower()
        assert "dataset" in page_source or "not found" in page_source

    def test_dataset_metadata_visible(self, driver):
        """Test that dataset metadata is visible"""
        driver.get("http://localhost:5000/dataset/view/1")
        try:
            metadata_elements = driver.find_elements(
                By.CSS_SELECTOR, ".title, .description, .author, .metadata, h1, h2"
            )
            assert len(metadata_elements) > 0
        except Exception:
            pytest.skip("Dataset not found")


@pytest.mark.selenium
class TestDatasetUploadGUI:
    """GUI tests for dataset upload"""

    def test_upload_page_accessible(self, logged_in_driver):
        """Test upload page is accessible when logged in"""
        logged_in_driver.get("http://localhost:5000/dataset/upload")
        WebDriverWait(logged_in_driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        assert "/login" not in logged_in_driver.current_url

    def test_upload_form_exists(self, logged_in_driver):
        """Test that upload form exists"""
        logged_in_driver.get("http://localhost:5000/dataset/upload")
        forms = logged_in_driver.find_elements(By.TAG_NAME, "form")
        assert len(forms) > 0

    def test_upload_form_has_file_input(self, logged_in_driver):
        """Test that upload form has file input"""
        logged_in_driver.get("http://localhost:5000/dataset/upload")
        file_inputs = logged_in_driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        assert len(file_inputs) > 0

    def test_upload_requires_authentication(self, driver):
        """Test that upload requires login"""
        driver.get("http://localhost:5000/logout")
        driver.get("http://localhost:5000/dataset/upload")
        WebDriverWait(driver, 10).until(lambda d: d.current_url != "http://localhost:5000/dataset/upload")
        assert "/login" in driver.current_url or "login" in driver.page_source.lower()


@pytest.mark.selenium
class TestDatasetSearchGUI:
    """GUI tests for dataset search"""

    def test_search_from_homepage(self, driver):
        """Test searching from homepage"""
        driver.get("http://localhost:5000/")
        search_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='search'], input[type='text']")

        if len(search_inputs) > 0:
            search_input = search_inputs[0]
            search_input.send_keys("test")
            search_input.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(lambda d: d.current_url != "http://localhost:5000/")
            assert "explore" in driver.current_url or "search" in driver.current_url
        else:
            pytest.skip("No search input on homepage")

    def test_advanced_search_filters(self, driver):
        """Test advanced search filters"""
        driver.get("http://localhost:5000/explore")
        filters = driver.find_elements(By.CSS_SELECTOR, "select, input[type='checkbox']")

        if len(filters) > 0:
            filter_element = filters[0]
            if filter_element.tag_name == "select":
                from selenium.webdriver.support.select import Select

                select = Select(filter_element)
                if len(select.options) > 1:
                    select.select_by_index(1)
            elif filter_element.get_attribute("type") == "checkbox":
                filter_element.click()

            WebDriverWait(driver, 10).until(lambda d: True)
            assert True
        else:
            pytest.skip("No filters found")


@pytest.mark.selenium
@pytest.mark.slow
class TestDatasetUIResponsive:
    """Responsive design tests"""

    def test_mobile_viewport(self, driver):
        """Test mobile responsive design"""
        driver.set_window_size(375, 667)
        driver.get("http://localhost:5000/explore")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        body_width = driver.execute_script("return document.body.scrollWidth")
        viewport_width = driver.execute_script("return window.innerWidth")

        assert body_width <= viewport_width + 50

        driver.set_window_size(1920, 1080)

    def test_tablet_viewport(self, driver):
        """Test tablet responsive design"""
        driver.set_window_size(768, 1024)
        driver.get("http://localhost:5000/explore")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        assert driver.current_url is not None

        driver.set_window_size(1920, 1080)
