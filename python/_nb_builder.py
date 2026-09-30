"""Tiny helper to build valid nbformat-4 .ipynb files from plain strings."""
import json
import uuid


def _cell_id():
    return uuid.uuid4().hex[:8]


def md(text):
    return {"cell_type": "markdown", "id": _cell_id(), "metadata": {}, "source": _split(text)}


def code(text):
    return {"cell_type": "code", "id": _cell_id(), "execution_count": None, "metadata": {},
            "outputs": [], "source": _split(text)}


def _split(text):
    lines = text.strip("\n").split("\n")
    return [l + "\n" for l in lines[:-1]] + ([lines[-1]] if lines else [])


def write_notebook(path, cells):
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {"name": "python", "version": "3.x"}
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    with open(path, "w") as f:
        json.dump(nb, f, indent=1)
    print(f"wrote {path}")
