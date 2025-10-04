"""Ontology registry abstraction.

Defines a simple registry API and a default implementation that wraps the
existing LOAN_ONTOLOGY and PORTFOLIO_CONTEXT for backward compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol


class Ontology(Protocol):
    def get_domains(self) -> Dict[str, Any]:
        ...

    def get_portfolio_context(self) -> Dict[str, Any]:
        ...


@dataclass
class StaticOntology:
    domains: Dict[str, Any]
    portfolio_context: Dict[str, Any]

    def get_domains(self) -> Dict[str, Any]:
        return self.domains

    def get_portfolio_context(self) -> Dict[str, Any]:
        return self.portfolio_context


def get_default_ontology() -> StaticOntology:
    try:
        from src.data_dictionary import LOAN_ONTOLOGY, PORTFOLIO_CONTEXT

        return StaticOntology(LOAN_ONTOLOGY, PORTFOLIO_CONTEXT)
    except Exception:  # pragma: no cover
        return StaticOntology({}, {})


__all__ = ["Ontology", "StaticOntology", "get_default_ontology"]
