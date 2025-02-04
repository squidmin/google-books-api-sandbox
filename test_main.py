from unittest.mock import patch

import pytest

import config
from main import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_health(client):
    """Test the /health route."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.data == b"ok"


@patch('main.send_from_directory')
def test_send_content(mock_send_from_directory, client):
    """Test the /content/<path> route."""
    mock_send_from_directory.return_value = "Content fetched"
    response = client.get('/content/test_book.pdf')
    mock_send_from_directory.assert_called_once_with(config.CONTENT_BASE_DIR, 'test_book.pdf')
    assert response.data == b"Content fetched"
    assert response.status_code == 200
