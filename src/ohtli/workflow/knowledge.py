from __future__ import annotations


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
