"""Реализация CLI-утилиты `my-wc`."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True, slots=True)
class Counts:
    """Контейнер для количества строк, слов и байт."""
    lines: int
    words: int
    bytes: int


def count_data(data: bytes) -> Counts:
    """Подсчёт строк, слов и байт во входных данных."""
    return Counts(
        lines=data.count(b"\n"),
        words=len(data.split()),
        bytes=len(data),
    )


def read_bytes_from_path(path: Path) -> bytes:
    """Чтение всех байтов из файла."""
    return path.read_bytes()


def read_bytes_from_stdin() -> bytes:
    """Чтение всех байтов из стандартного ввода."""
    return sys.stdin.buffer.read()


def build_parser() -> argparse.ArgumentParser:
    """Создание парсера аргументов."""
    parser = argparse.ArgumentParser(
        prog="my-wc",
        description="Подсчёт строк, слов и байт в файлах или стандартном вводе.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-l", "--lines", action="store_true", help="вывести количество строк")
    group.add_argument("-w", "--words", action="store_true", help="вывести количество слов")
    group.add_argument("-c", "--bytes", action="store_true", help="вывести количество байт")
    parser.add_argument(
        "file",
        nargs="?",
        help="путь к файлу; если не указан или '-', читается stdin",
    )
    return parser


def format_output(counts: Counts, filename: str | None, args: argparse.Namespace) -> str:
    """Форматирование вывода (аналогично Unix wc)."""
    if args.lines:
        fields = [f"Количество строк: {counts.lines}"]
    elif args.words:
        fields = [f"Количество слов: {counts.words}"]
    elif args.bytes:
        fields = [f"Количество байт: {counts.bytes}"]
    else:
        fields = [
            f"Количество строк: {counts.lines}",
            f"Количество слов: {counts.words}",
            f"Количество байт: {counts.bytes}",
        ]

    if filename is not None:
        fields.append(f"Файл: {filename}")
    return " | ".join(fields)


def process_input(filename: str | None) -> tuple[Counts, str | None]:
    """Чтение данных из файла или stdin и подсчёт."""
    if filename is None or filename == "-":
        data = read_bytes_from_stdin()
        return count_data(data), None

    path = Path(filename)
    data = read_bytes_from_path(path)
    return count_data(data), filename


def main(argv: Sequence[str] | None = None) -> int:
    """Точка входа CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.file is None and sys.stdin.isatty():
        print("🤔 Ты вызвал my-wc... но что считать-то? Попробуй файл или stdin!", file=sys.stderr)
        parser.print_help()
        return 1

    try:
        counts, filename = process_input(args.file)
    except FileNotFoundError:
        parser.exit(1, f"my-wc: {args.file}: Файл не найден\n")
    except PermissionError:
        parser.exit(1, f"my-wc: {args.file}: Нет доступа\n")
    except OSError as exc:
        parser.exit(1, f"my-wc: {args.file}: {exc}\n")

    print(format_output(counts, filename, args))
    return 0