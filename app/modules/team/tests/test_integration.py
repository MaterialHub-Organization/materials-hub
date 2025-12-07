"""
Integration tests for team module.
"""

import pytest


@pytest.mark.integration
def test_team_page_loads(test_client):
    """Test that the team page loads successfully."""
    response = test_client.get("/team")
    assert response.status_code == 200


@pytest.mark.integration
def test_team_page_content(test_client):
    """Test that the team page contains expected content."""
    response = test_client.get("/team")
    assert response.status_code == 200
    # Check for common team-related content
    assert b"team" in response.data.lower() or b"about" in response.data.lower()


@pytest.mark.integration
def test_team_page_no_authentication_required(test_client):
    """Test that the team page doesn't require authentication."""
    # Access without logging in
    response = test_client.get("/team")
    assert response.status_code == 200
    # Should not redirect to login
    assert response.request.path == "/team"
