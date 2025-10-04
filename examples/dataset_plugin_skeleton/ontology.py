from dataclasses import dataclass
from typing import Any, Dict

from conversql.ontology.registry import StaticOntology


def make_ontology() -> StaticOntology:
    # Replace with your domain ontology
    return StaticOntology(domains={}, portfolio_context={})
