"""UI package exports.

Historically this package exposed multiple tab render functions via a `tabs.py` module.
That module has been removed during the visualization layer refactor; importing it now
causes a ModuleNotFoundError at application startup. We keep the public surface area
minimal here and only re-export stable helpers actually present.
"""

from .components import display_results, format_file_size, render_section_header

__all__ = ["display_results", "format_file_size", "render_section_header"]
