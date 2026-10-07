"""`slugify` turns a title into a note's file name stem (#157).

The old version kept only `[a-z0-9]`, dropping every accented or non-Latin
character: "Café" -> "caf", "Artículo sobre caché distribuido" ->
"art-culo-sobre-cach-distribuido" (a real file in the vault). The new
version normalizes with NFKD first (splitting an accented letter into its
base letter plus a combining mark, and folding compatibility forms --
ligatures, full-width, math-styled letters), drops the combining marks,
then casefolds -- in that order, so a character that only becomes an
ordinary letter after NFKD (e.g. a math-bold capital) is not lost by an
earlier casefold.

Changing `slugify` affects only the file name chosen for a NEW note.
Existing notes are always located by title (`find_notes_titled`), never by
recomputing their slug -- confirmed for one representative operation in
`tests/test_execution_legacy_slug_location.py`.
"""

import re

import pytest

from ohtli.vault_io.paths import slugify


@pytest.mark.parametrize(
    "title,expected",
    [
        ("Foo Bar", "foo-bar"),
        ("foo-bar", "foo-bar"),
        ("  Trimmed  ", "trimmed"),
        ("2026-07-29 14:30", "2026-07-29-14-30"),
        ("Index Fund", "index-fund"),
        ("README", "readme"),
        ("!!!", "untitled"),
        ("", "untitled"),
    ],
)
def test_ascii_titles_slugify_exactly_as_before(title, expected):
    assert slugify(title) == expected


@pytest.mark.parametrize(
    "title,expected",
    [
        ("Café", "cafe"),
        ("Artículo sobre caché distribuido", "articulo-sobre-cache-distribuido"),
        ("Standup rápido", "standup-rapido"),
        ("¿Qué pasó?", "que-paso"),
        ("Año nuevo", "ano-nuevo"),
        ("İstanbul", "istanbul"),
    ],
)
def test_accented_latin_titles_are_transliterated(title, expected):
    """The two real files this issue was opened about, and other everyday
    Spanish titles: accents are dropped, not the whole word."""
    assert slugify(title) == expected


@pytest.mark.parametrize(
    "title,expected",
    [
        ("ﬁle", "file"),  # the "fi" ligature (U+FB01)
        ("ＡＢＣ", "abc"),  # full-width Latin
        ("𝐀𝐁𝐂", "abc"),  # mathematical bold capitals
        ("ℌello", "hello"),  # black-letter capital H (U+210C)
        ("x²", "x2"),  # superscript digit
        ("Straße", "strasse"),  # German eszett decomposes under NFKD
    ],
)
def test_compatibility_forms_fold_to_ascii(title, expected):
    """Guards the order of operations: casefold runs AFTER NFKD, because
    some of these characters have no lowercase mapping of their own and are
    only ordinary ASCII letters once normalized. Casefolding first would
    lose them (e.g. the bold capitals would fall straight to 'untitled')."""
    assert slugify(title) == expected


def test_precomposed_and_decomposed_accents_share_a_slug():
    """"Café" with the accent as its own Unicode code point (NFC, what a
    person normally types) and with the accent as a separate combining
    character (NFD, what some input methods or macOS can produce) must
    slugify identically."""
    precomposed = "Café"
    decomposed = "Café"
    assert precomposed != decomposed
    assert slugify(precomposed) == slugify(decomposed) == "cafe"


@pytest.mark.parametrize(
    "title",
    [
        "Привет мир",
        "Καφές",
        "会議メモ",
        "مرحبا",
        "🚀🔥",
        "!!!",
    ],
)
def test_titles_without_latin_letters_or_digits_fall_back_to_untitled(title):
    """NFKD does nothing useful for scripts with no Latin decomposition
    (Cyrillic, Greek, CJK, Arabic) or for symbols/emoji -- unchanged from
    before this fix. One such note per folder is still fine; the next one
    is refused as `same_file_name`, never silently overwritten."""
    assert slugify(title) == "untitled"


@pytest.mark.parametrize(
    "title",
    [
        "Foo Bar",
        "Café",
        "Artículo sobre caché distribuido",
        "¿Qué pasó?",
        "ﬁle",
        "x²",
    ],
)
def test_every_slug_is_ascii_kebab_case(title):
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slugify(title))
