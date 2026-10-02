"""Command-line entry points, installed by `pip install -e .` (pyproject.toml):

    lunaxx-register <source> <reference> --out <dir>    register one pair, export the deliverables
    lunaxx-find-reference <chandrayaan-2 product id>   the images covering it, best Sun first
    lunaxx-workbench                                   the registration workbench in a browser

Each is exactly `python -m core.pipeline`, `python -m ops.find_reference` and `python -m web.server`.
"""
import sys


def register() -> int:
    from core.pipeline import main
    return main(sys.argv[1:])


def find_reference() -> int:
    from ops.find_reference import main
    return main(sys.argv[1:])


def workbench() -> int:
    from web.server import main
    return main(sys.argv[1:])
