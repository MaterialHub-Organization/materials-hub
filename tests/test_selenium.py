"""
Consolidated selenium/interface tests for all modules.
"""
import os  # noqa: F401, F811, E402
import pytest
import time  # noqa: F401, F811

import pytest
from selenium.common.exceptions import NoSuchElementException  # noqa: F401, F811
from selenium.webdriver.common.by import By  # noqa: F401, F811
from selenium.webdriver.common.keys import Keys  # noqa: F401, F811

from core.environment.host import get_host_for_selenium_testing  # noqa: F401, F811
from core.selenium.common import close_driver, initialize_driver  # noqa: F401, F811

# ============================================================================
# Tests from app/modules/auth/tests/test_selenium.py
# ============================================================================

Consolidated selenium/interface tests for all modules.
# ============================================================================
# Tests from app/modules/auth/tests/test_selenium.py
# ============================================================================

@pytest.mark.selenium

def test_login_and_check_element():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        driver.get(f"{host}/login")

        time.sleep(4)

        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")

        password_field.send_keys(Keys.RETURN)

        time.sleep(4)

        try:
            driver.find_element(By.XPATH, "//a[contains(@href, '/logout')]")
            driver.find_element(By.XPATH, "//span[contains(text(), 'Doe, John')]")
            print("Test passed!")

        except NoSuchElementException:
            raise AssertionError("Test failed!")

    finally:

        close_driver(driver)


# ============================================================================

# ============================================================================

@pytest.mark.selenium

def test_hubfile_index():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        driver.get(f"{host}/hubfile")

        time.sleep(4)

        try:

            pass

        except NoSuchElementException:
            raise AssertionError("Test failed!")

    finally:

        close_driver(driver)


# ============================================================================

# ============================================================================

@pytest.mark.selenium

def test_flamapy_index():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        driver.get(f"{host}/flamapy")

        time.sleep(4)

        try:

            pass

        except NoSuchElementException:
            raise AssertionError("Test failed!")

    finally:

        close_driver(driver)


# ============================================================================

# ============================================================================

@pytest.mark.selenium

def test_featuremodel_index():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        driver.get(f"{host}/featuremodel")

        time.sleep(4)

        try:

            pass

        except NoSuchElementException:
            raise AssertionError("Test failed!")

    finally:

        close_driver(driver)


# ============================================================================

# ============================================================================

@pytest.mark.selenium

def test_webhook_index():

    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        driver.get(f"{host}/webhook")

        time.sleep(4)

        try:

            pass

        except NoSuchElementException:
            raise AssertionError("Test failed!")

    finally:

        close_driver(driver)


# ============================================================================

# ============================================================================

def wait_for_page_to_load(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
    except Exception:
        time.sleep(2)


def count_datasets(driver, host):
    driver.get(f"{host}/dataset/list")
    wait_for_page_to_load(driver)

    try:
        amount_datasets = len(driver.find_elements(By.XPATH, "//table//tbody//tr"))
    except Exception:
        amount_datasets = 0
    return amount_datasets


@pytest.mark.selenium

def test_upload_dataset():
    driver = initialize_driver()

    try:
        host = get_host_for_selenium_testing()

        driver.get(f"{host}/login")
        wait_for_page_to_load(driver)

        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")

        email_field.send_keys("user1@example.com")
        password_field.send_keys("1234")

        password_field.send_keys(Keys.RETURN)
        time.sleep(6)  # Wait longer for login redirect

        initial_datasets = count_datasets(driver, host)

        driver.get(f"{host}/dataset/upload")
        wait_for_page_to_load(driver)

        title_field = driver.find_element(By.NAME, "title")
        title_field.send_keys("Title")
        desc_field = driver.find_element(By.NAME, "desc")
        desc_field.send_keys("Description")
        tags_field = driver.find_element(By.NAME, "tags")
        tags_field.send_keys("tag1,tag2")

        add_author_button = driver.find_element(By.ID, "add_author")
        add_author_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)
        add_author_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        name_field0 = driver.find_element(By.NAME, "authors-0-name")
        name_field0.send_keys("Author0")
        affiliation_field0 = driver.find_element(By.NAME, "authors-0-affiliation")
        affiliation_field0.send_keys("Club0")
        orcid_field0 = driver.find_element(By.NAME, "authors-0-orcid")
        orcid_field0.send_keys("0000-0000-0000-0000")

        name_field1 = driver.find_element(By.NAME, "authors-1-name")
        name_field1.send_keys("Author1")
        affiliation_field1 = driver.find_element(By.NAME, "authors-1-affiliation")
        affiliation_field1.send_keys("Club1")

        file1_path = os.path.abspath("app/modules/dataset/uvl_examples/file1.uvl")
        file2_path = os.path.abspath("app/modules/dataset/uvl_examples/file2.uvl")

        time.sleep(3)

        try:
            dropzone = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "dz-hidden-input"))
            )
        except Exception:
            time.sleep(2)
            dropzone = driver.find_element(By.CSS_SELECTOR, "input[type='file']")

        dropzone.send_keys(file1_path)
        time.sleep(2)

        try:
            dropzone = driver.find_element(By.CLASS_NAME, "dz-hidden-input")
        except Exception:
            dropzone = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        dropzone.send_keys(file2_path)

        time.sleep(5)

        show_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "0_button"))
        )
        show_button.send_keys(Keys.RETURN)
        add_author_uvl_button = driver.find_element(By.ID, "0_form_authors_button")
        add_author_uvl_button.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)

        name_field = driver.find_element(By.NAME, "feature_models-0-authors-2-name")
        name_field.send_keys("Author3")
        affiliation_field = driver.find_element(By.NAME, "feature_models-0-authors-2-affiliation")
        affiliation_field.send_keys("Club3")

        check = driver.find_element(By.ID, "agreeCheckbox")
        check.send_keys(Keys.SPACE)
        wait_for_page_to_load(driver)

        upload_btn = driver.find_element(By.ID, "upload_button")
        upload_btn.send_keys(Keys.RETURN)
        wait_for_page_to_load(driver)
        time.sleep(2)  # Force wait time

        assert driver.current_url == f"{host}/dataset/list", "Test failed!"

        final_datasets = count_datasets(driver, host)
        assert final_datasets == initial_datasets + 1, "Test failed!"

        print("Test passed!")

    finally:

        close_driver(driver)
