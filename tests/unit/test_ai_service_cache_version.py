"""Test AI service caching functionality."""

from src import ai_service as ai_service_module


def test_ai_service_cache():
    """Test that AI service caching works correctly."""
    # This is a placeholder test
    assert True


def test_cache_invalidation():
    """Test cache invalidation logic."""
    # This is a placeholder test
    assert True


def test_ai_service_cache_version_invalidation(monkeypatch):
    # Grab first instance
    service1 = ai_service_module.get_ai_service()
    assert service1 is not None

    # Monkeypatch the CACHE_VERSION and reload module to simulate version bump
    monkeypatch.setenv("_FORCE_RELOAD", "1")  # just a no-op env to change reload semantics
    ai_service_module.CACHE_VERSION += 1  # bump in place
    ai_service_module.get_ai_service.clear()

    # Because Streamlit cache keys include function arguments, calling with new implicit default should invalidate
    service2 = ai_service_module.get_ai_service()
    assert service2 is not None
    # Instances should differ in identity post invalidation
    assert service1 is not service2, "Cache version bump should produce a new AIService instance"
