import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to sys.path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Define mocks
mock_fill_mask = MagicMock()
mock_sentiment = MagicMock()

# Configure fill_mask mock
def fill_mask_side_effect(text):
    return [
        {'sequence': text.replace('[MASK]', 'good'), 'token_str': 'good'},
        {'sequence': text.replace('[MASK]', 'bad'), 'token_str': 'bad'}
    ]
mock_fill_mask.side_effect = fill_mask_side_effect
mock_fill_mask.tokenizer.mask_token = '[MASK]'

# Configure sentiment_analysis mock
def sentiment_side_effect(sequence):
    if 'good' in sequence:
        return [{'label': 'POSITIVE'}]
    return [{'label': 'NEGATIVE'}]
mock_sentiment.side_effect = sentiment_side_effect

# Configure pipeline factory
def pipeline_side_effect(task, model=None):
    if task == "fill-mask":
        return mock_fill_mask
    if task == "sentiment-analysis":
        return mock_sentiment
    return MagicMock()

# Create a mock for transformers module
mock_transformers = MagicMock()
mock_transformers.pipeline.side_effect = pipeline_side_effect

# Setup mock cache
mock_cache_cls = MagicMock()
mock_cache_instance = MagicMock()
mock_cache_cls.return_value = mock_cache_instance
mock_cache_instance.get.return_value = None

# Patch modules
# We need to patch 'transformers' and 'diskcache' in sys.modules
# because app.py imports them at top level.

with patch.dict(sys.modules, {
    'transformers': mock_transformers,
    'diskcache': MagicMock(Cache=mock_cache_cls)
}):
    # Verify transformers is mocked
    import transformers
    assert isinstance(transformers, MagicMock)

    # Verify diskcache is mocked
    import diskcache
    assert diskcache.Cache == mock_cache_cls

    # Now import app
    if 'app' in sys.modules:
        del sys.modules['app']

    import app
    from fastapi.testclient import TestClient

    def test_get_suggestions_success():
        # Use TestClient as context manager to trigger lifespan
        with TestClient(app.app) as client:
            # Reset cache mock
            mock_cache_instance.get.return_value = None
            mock_cache_instance.set.reset_mock()

            response = client.post("/suggestions/", json={"sentence": "have a <blank> day"})
            assert response.status_code == 200
            data = response.json()
            assert "suggestions" in data
            assert "good" in data["suggestions"]
            assert "bad" not in data["suggestions"]

            mock_cache_instance.set.assert_called_with("have a <blank> day", ["good"])

    def test_get_suggestions_invalid_input():
        with TestClient(app.app) as client:
            response = client.post("/suggestions/", json={"sentence": "have a nice day"})
            assert response.status_code == 400
            assert response.json()["detail"] == "Input must contain '<blank>'"

    def test_get_suggestions_cache_hit():
        with TestClient(app.app) as client:
            mock_cache_instance.get.return_value = ["cached_good"]

            response = client.post("/suggestions/", json={"sentence": "have a <blank> day"})
            assert response.status_code == 200
            assert response.json()["suggestions"] == ["cached_good"]

    def test_health_check():
        with TestClient(app.app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}
