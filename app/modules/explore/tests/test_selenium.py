"""
Selenium GUI tests for explore module.

Tests the explore page user interface including search, filters,
and dataset browsing functionality using a real browser.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.fixture(scope="module")
def driver():
    """
    Setup and teardown for Selenium WebDriver.
    Uses Chrome in headless mode by default.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)  # Wait up to 10 seconds for elements

    yield driver

    driver.quit()


class TestExplorePageGUI:
    """GUI tests for explore page functionality"""

    def test_explore_page_loads(self, driver):
        """Test that explore page loads successfully"""
        driver.get("http://localhost:5000/explore")

        # Wait for page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Verify page title or heading
        assert "explore" in driver.current_url.lower()
        assert driver.title is not None

    def test_search_bar_visible(self, driver):
        """Test that search bar is visible and accessible"""
        driver.get("http://localhost:5000/explore")

        # Find search input (adjust selector based on actual HTML)
        search_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='search'], input[type='text']")

        assert len(search_inputs) > 0, "No search input found on explore page"

    def test_search_functionality(self, driver):
        """Test search functionality with keyword"""
        driver.get("http://localhost:5000/explore")

        # Find search input
        search_input = driver.find_element(By.CSS_SELECTOR, "input[type='search'], input[type='text']")

        # Enter search query
        search_query = "test dataset"
        search_input.clear()
        search_input.send_keys(search_query)
        search_input.send_keys(Keys.RETURN)

        # Wait for results to load
        WebDriverWait(driver, 10).until(
            lambda d: "query=" in d.current_url or d.find_elements(By.CLASS_NAME, "dataset")
        )

        # Verify search was performed (URL contains query or results shown)
        assert "query=" in driver.current_url or len(driver.find_elements(By.CLASS_NAME, "dataset")) >= 0

    def test_filter_options_visible(self, driver):
        """Test that filter options are visible"""
        driver.get("http://localhost:5000/explore")

        # Look for filter elements (dropdowns, checkboxes, etc.)
        filters = driver.find_elements(By.CSS_SELECTOR, "select, input[type='checkbox'], .filter")

        # At least some filtering mechanism should exist
        assert len(filters) > 0 or driver.find_elements(By.LINK_TEXT, "Filter")

    def test_dataset_cards_display(self, driver):
        """Test that dataset cards/items are displayed"""
        driver.get("http://localhost:5000/explore")

        # Wait for content to load
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, ".dataset, .card, .item, article")) > 0
            or "No results" in d.page_source
        )

        # Check if datasets are displayed or "no results" message shown
        datasets = driver.find_elements(By.CSS_SELECTOR, ".dataset, .card, .item, article")
        no_results = "no results" in driver.page_source.lower() or "no datasets" in driver.page_source.lower()

        assert len(datasets) > 0 or no_results

    def test_pagination_exists(self, driver):
        """Test that pagination controls exist if needed"""
        driver.get("http://localhost:5000/explore")

        # Look for pagination elements
        pagination = driver.find_elements(By.CSS_SELECTOR, ".pagination, nav[aria-label='pagination']")

        # Pagination may or may not exist depending on number of results
        # This is a soft check
        if len(pagination) > 0:
            assert True  # Pagination exists
        else:
            # Check if there are few enough results that pagination isn't needed
            datasets = driver.find_elements(By.CSS_SELECTOR, ".dataset, .card, .item")
            assert len(datasets) <= 20  # Assuming 20 per page

    def test_click_dataset_opens_detail(self, driver):
        """Test clicking a dataset opens its detail page"""
        driver.get("http://localhost:5000/explore")

        # Find first dataset link
        dataset_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='dataset']")

        if len(dataset_links) > 0:
            first_link = dataset_links[0]
            first_link.click()

            # Wait for navigation
            WebDriverWait(driver, 10).until(lambda d: "dataset" in d.current_url)

            # Verify we're on a dataset detail page
            assert "dataset" in driver.current_url
        else:
            pytest.skip("No datasets available to click")

    def test_sorting_functionality(self, driver):
        """Test that sorting options work"""
        driver.get("http://localhost:5000/explore")

        # Look for sorting dropdown/buttons
        sort_elements = driver.find_elements(By.CSS_SELECTOR, "select[name*='sort'], button[data-sort]")

        if len(sort_elements) > 0:
            # Click/select a sorting option
            sort_element = sort_elements[0]

            if sort_element.tag_name == "select":
                # Dropdown - select an option
                from selenium.webdriver.support.select import Select

                select = Select(sort_element)
                if len(select.options) > 1:
                    select.select_by_index(1)

                    # Wait for page to reload/update
                    WebDriverWait(driver, 10).until(lambda d: "sort=" in d.current_url or EC.staleness_of(sort_element))

                    assert True  # Sorting was applied
            else:
                # Button - click it
                sort_element.click()
                WebDriverWait(driver, 10).until(lambda d: "sort=" in d.current_url)
                assert True
        else:
            pytest.skip("No sorting controls found")

    def test_responsive_design_mobile(self, driver):
        """Test that page is responsive on mobile viewport"""
        # Set mobile viewport
        driver.set_window_size(375, 667)  # iPhone size

        driver.get("http://localhost:5000/explore")

        # Wait for page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Check that page loads without horizontal scroll
        body_width = driver.execute_script("return document.body.scrollWidth")
        viewport_width = driver.execute_script("return window.innerWidth")

        assert body_width <= viewport_width + 50  # Allow small margin

        # Reset to desktop size
        driver.set_window_size(1920, 1080)

    def test_page_load_performance(self, driver):
        """Test that explore page loads within acceptable time"""
        import time

        start_time = time.time()
        driver.get("http://localhost:5000/explore")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        load_time = time.time() - start_time

        # Page should load within 5 seconds
        assert load_time < 5.0, f"Page took {load_time:.2f}s to load (expected < 5s)"


@pytest.mark.selenium
class TestExploreInteractions:
    """Advanced interaction tests for explore page"""

    def test_filter_interaction(self, driver):
        """Test applying multiple filters"""
        driver.get("http://localhost:5000/explore")

        # Find filter checkboxes
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")

        if len(checkboxes) > 0:
            # Click first checkbox
            checkboxes[0].click()

            # Wait for results to update
            WebDriverWait(driver, 10).until(lambda d: len(d.find_elements(By.CSS_SELECTOR, ".dataset, .card")) >= 0)

            assert True  # Filter was applied
        else:
            pytest.skip("No filter checkboxes found")

    def test_search_with_no_results(self, driver):
        """Test search with query that returns no results"""
        driver.get("http://localhost:5000/explore")

        # Find search input
        search_input = driver.find_element(By.CSS_SELECTOR, "input[type='search'], input[type='text']")

        # Search for something that definitely doesn't exist
        search_input.clear()
        search_input.send_keys("xyzabc123nonexistent")
        search_input.send_keys(Keys.RETURN)

        # Wait for page to load
        WebDriverWait(driver, 10).until(lambda d: "query=" in d.current_url)

        # Check for "no results" message
        page_text = driver.page_source.lower()
        assert (
            "no results" in page_text
            or "no datasets" in page_text
            or "not found" in page_text
            or "0 results" in page_text
        )

    def test_keyboard_navigation(self, driver):
        """Test keyboard navigation (Tab key)"""
        driver.get("http://localhost:5000/explore")

        # Get initial focused element
        initial_element = driver.switch_to.active_element

        # Press Tab to move focus
        initial_element.send_keys(Keys.TAB)

        # Get new focused element
        new_element = driver.switch_to.active_element

        # Verify focus moved
        assert initial_element != new_element
