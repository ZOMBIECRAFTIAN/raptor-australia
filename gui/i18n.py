"""
Lightweight internationalisation (i18n) for the Flask app.

Loads one JSON file per language from ``gui/translations/``,
exposes a ``t(key)`` helper that resolves dotted-path lookups
with English fallback when a key is missing in the current
language. Persists the user's choice via cookie.

The 10 supported languages match the project specification:
en, es, fr, pt, it, de, zh, ko, ru, ja.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flask import request

TRANSLATIONS_DIR = Path(__file__).parent / "translations"
DEFAULT_LANG     = "en"
COOKIE_NAME      = "raptor_lang"

# Language registry: code → display metadata.
# Order here is the order shown in the picker dropdown.
LANGUAGES: dict[str, dict[str, str]] = {
    "en": {"name": "English",   "native": "English",     "flag": "🇬🇧"},
    "es": {"name": "Spanish",   "native": "Español",     "flag": "🇪🇸"},
    "fr": {"name": "French",    "native": "Français",    "flag": "🇫🇷"},
    "pt": {"name": "Portuguese","native": "Português",   "flag": "🇵🇹"},
    "it": {"name": "Italian",   "native": "Italiano",    "flag": "🇮🇹"},
    "de": {"name": "German",    "native": "Deutsch",     "flag": "🇩🇪"},
    "zh": {"name": "Chinese",   "native": "中文",         "flag": "🇨🇳"},
    "ko": {"name": "Korean",    "native": "한국어",        "flag": "🇰🇷"},
    "ja": {"name": "Japanese",  "native": "日本語",        "flag": "🇯🇵"},
    "ru": {"name": "Russian",   "native": "Русский",      "flag": "🇷🇺"},
}

# Loaded translations cache.
_TRANSLATIONS: dict[str, dict[str, Any]] = {}


def _load_one(code: str) -> dict[str, Any]:
    path = TRANSLATIONS_DIR / f"{code}.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_translations() -> None:
    """Eagerly load every language file at startup."""
    _TRANSLATIONS.clear()
    for code in LANGUAGES:
        _TRANSLATIONS[code] = _load_one(code)


def get_locale() -> str:
    """
    Resolve the current locale, in priority order:
    1. ``?lang=xx`` query param (one-shot override),
    2. ``raptor_lang`` cookie,
    3. ``Accept-Language`` HTTP header,
    4. Default (English).
    """
    qlang = (request.args.get("lang") or "").lower()
    if qlang in LANGUAGES:
        return qlang

    clang = (request.cookies.get(COOKIE_NAME) or "").lower()
    if clang in LANGUAGES:
        return clang

    accept = (request.accept_languages.best_match(list(LANGUAGES))
              if request.accept_languages else None)
    if accept:
        return accept

    return DEFAULT_LANG


def _walk(d: dict, dotted: str) -> Any:
    """Resolve `'a.b.c'` against a nested dict; return None if missing."""
    cur: Any = d
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def t(key: str, **format_args: Any) -> str:
    """
    Translate ``key`` (a dotted path like ``'home.title'``) into the
    current locale, falling back to English, then to the literal key.

    Optional ``format_args`` perform Python ``str.format`` substitution
    on the resolved string, e.g. ``t('greet', name='Brian')``.
    """
    lang = get_locale()

    primary  = _walk(_TRANSLATIONS.get(lang, {}),         key)
    fallback = _walk(_TRANSLATIONS.get(DEFAULT_LANG, {}), key)
    value    = primary if isinstance(primary, str) and primary else fallback
    if not isinstance(value, str) or not value:
        value = key

    if format_args:
        try:
            value = value.format(**format_args)
        except (KeyError, IndexError, ValueError):
            pass
    return value


def get_languages() -> dict[str, dict[str, str]]:
    """Expose LANGUAGES dict to the templates."""
    return LANGUAGES
