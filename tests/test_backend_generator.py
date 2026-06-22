import pytest
from unittest.mock import MagicMock
from backend.generator import BackendGenerator

def test_backend_generator_outputs():
    # Mock settings and model manager
    mock_settings = MagicMock()
    mock_model_manager = MagicMock()
    
    generator = BackendGenerator(mock_settings, mock_model_manager)
    
    # Run generator with a simple configuration
    features = ["auth", "database"]
    architecture = {
        "api_routes": ["users", "posts"]
    }
    
    files = generator.generate("saas", features, architecture)
    
    # Assert expected files are in the output dictionary
    assert "backend/main.py" in files
    assert "backend/config.py" in files
    assert "backend/database.py" in files
    assert "backend/requirements.txt" in files
    assert "backend/routes/users.py" in files
    assert "backend/routes/posts.py" in files
    
    # Assert generated contents are valid
    assert "router = APIRouter(prefix=\"/users\"" in files["backend/routes/users.py"]
    assert "class UserCreate(BaseModel):" in files["backend/routes/users.py"]
    assert "app = FastAPI(" in files["backend/main.py"]
