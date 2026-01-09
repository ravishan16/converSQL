from typing import Dict, Optional

from .base import AIEngine

_registry: Dict[str, AIEngine] = {}
_default_engine: Optional[str] = None


def register(name: str, engine: AIEngine, is_default: bool = False):
    """Register an AI engine."""
    _registry[name] = engine
    if is_default:
        global _default_engine
        _default_engine = name


def get(name: str) -> Optional[AIEngine]:
    """Get an AI engine by name."""
    return _registry.get(name)


def get_default() -> Optional[AIEngine]:
    """Get the default AI engine."""
    if _default_engine:
        return get(_default_engine)
    return None


def get_available_engines() -> list[str]:
    """Get a list of available engine names."""
    return list(_registry.keys())

def set_default(name: str):
    """Set the default AI engine."""
    global _default_engine
    if name in _registry:
        _default_engine = name

def clear():
    """Clear the registry."""
    global _registry, _default_engine
    _registry = {}
    _default_engine = None

def register_all():
    """Register all available AI engines."""
    clear()
    from . import impl_claude, impl_gemini
    impl_claude.register_engine()
    impl_gemini.register_engine()
