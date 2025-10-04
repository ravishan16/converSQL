"""Dynamic plugin loader utilities."""

from __future__ import annotations

import importlib
from typing import Any, Callable


def load_callable(dotted: str) -> Callable[..., Any]:
    """Load a callable from a dotted path of the form 'package.module:func'.

    Raises ImportError or AttributeError if not found.
    """
    if ":" in dotted:
        module_name, func_name = dotted.split(":", 1)
    else:
        # Support dotted.attr; take last segment as attribute
        parts = dotted.rsplit(".", 1)
        if len(parts) != 2:
            raise ImportError(f"Invalid dotted path: {dotted}")
        module_name, func_name = parts
    module = importlib.import_module(module_name)
    fn = getattr(module, func_name)
    if not callable(fn):
        raise TypeError(f"Loaded object is not callable: {dotted}")
    return fn


__all__ = ["load_callable"]
