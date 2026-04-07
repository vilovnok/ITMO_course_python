"""Точка входа модуля для `python -m my_wc` и консольного скрипта."""

from __future__ import annotations

from .cmd import main


if __name__ == "__main__":
    raise SystemExit(main())
