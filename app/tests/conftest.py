import pytest
from starlette.testclient import TestClient

from main import app

USERNAME = "test2"
USER_PASSWORD = "b"


@pytest.fixture(scope="module")
def test_client():
    """
    Return an API Client
    """
    client = TestClient(app)

    client.auth = (USERNAME, USER_PASSWORD)

    yield TestClient(app)
