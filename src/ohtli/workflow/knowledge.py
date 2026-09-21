from __future__ import annotations

# The Domain Objects Knowledge may enrich when it Externalizes Developed
# Understanding. `knowledge-workflow.md` names exactly these three, each time
# without exception ("Output", "Domain Enrichment", "Externalize"). Reference,
# Meeting and Journal Entry are Knowledge *inputs* (sources of understanding),
# never enrichment targets.
EXTERNALIZE_TARGETS = ("Project", "Area", "Resource")


def is_externalize_target(domain_type_name: str) -> bool:
    """Whether a Domain Object type may be enriched by Externalize.

    Pure and independent from the actor. Takes the Domain Object's type
    name (as the Interaction Model table in `processing.py` does), so
    this module needs no other workflow and no Domain import.
    """
    return domain_type_name in EXTERNALIZE_TARGETS


def is_applicable(understanding: str, provenance: tuple[str, ...]) -> bool:
    """Knowledge's Externalize is applicable only when there is
    something to persist: non-empty understanding, with its epistemic
    provenance made explicit (`Epistemic Provenance`).

    Explore/Extract/Connect/Synthesize happen outside Ohtli's code —
    there is no `transform()` here, mirroring `evaluation.py` and
    `archive.py`'s precedent for operations Ohtli does not itself
    perform.
    """
    return bool(understanding.strip()) and bool(provenance) and all(p.strip() for p in provenance)
