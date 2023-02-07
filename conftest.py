from app import app
import pytest

@pytest.fixture
def api(monkeypatch):
    client = app.test_client()
    return client
