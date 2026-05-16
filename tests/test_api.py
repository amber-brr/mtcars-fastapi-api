"""
test_api.py

Automated tests for FastAPI app.

- test `/health`
- test readiness endpoint
- test one successful `/predict` request
- test invalid input
- test missing field behavior
"""
# -- API Access Setup --

# Tell Python where project root is before it tries to import app.main
import sys # modifies Python's import search path
from pathlib import Path # helps build file paths

# Finds root folder of project -> mtcars-fastapi/tests/test_api.py
# -> '__file__' means current file
# -> 'Path(__file__).resolve()' turns that into the full absolute path
# -> '.parents[1]' goes up two levels 
# --> parents[0] = /mnt/c/Users/<NAME>/Documents/mtcars-fastapi/tests
# --> parents[1] = /mnt/c/Users/<NAME>/Documents/mtcars-fastapi
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Adds project root to Python's import path
# -> Python uses 'sys.path' as a list of folders to search when import something
# -> '0' puts this path at front of search list so Python checks project folder first
sys.path.insert(0, str(PROJECT_ROOT))

# Add project root dir to Python's import path


# -- API Tests --

from fastapi.testclient import TestClient
from app.main import app

def test_health():
    """Test that the health endpoint returns success."""

    # Use TestClient(app) as client
    # -> makes FastAPI run startup code before test and shutdown code after 
    # -> model gets loaded during test, just like when the API runs normally
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_ready():
    """Test that the readiness endpoint returns success."""
    with TestClient(app) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}

def test_predict():
    """Test a successful prediction request."""
    request = {'wt': 2.62,'qsec': 16.46,'am': 1}

    with TestClient(app) as client:
        response = client.post("/predict", json=request)

    assert response.status_code == 200

    data = response.json()

    assert 'predicted_mpg' in data
    assert 'model_version' in data
    assert isinstance(data['predicted_mpg'], float)
    assert data['model_version'] == 'v1.0'

def test_invalid_wt():
    """Test that wt must be greater than 0."""
    request = {'wt': -2.62,'qsec': 16.46,'am': 1} #wt<0

    with TestClient(app) as client:
        response = client.post("/predict", json=request)

    assert response.status_code == 422

def test_invalid_qsec():
    """Test that qsec must be greater than 0."""
    request = {'wt': 2.62,'qsec': -16.46,'am': 1} #qsec<0

    with TestClient(app) as client:
        response = client.post("/predict", json=request)

    assert response.status_code == 422

def test_invalid_am():
    """Test that am must be binary 0 or 1."""
    request = {'wt': 2.62,'qsec': 16.46,'am': 2} #am is 2
    
    with TestClient(app) as client:
        response = client.post("/predict", json=request)
    
    assert response.status_code == 422

def test_missing_field():
    """Test missing required predictor field."""
    request = {'wt': 2.62,'qsec': 16.46} #no am
    
    with TestClient(app) as client:
        response = client.post("/predict", json=request)
    
    assert response.status_code == 422