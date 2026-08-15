#!/bin/bash
python3 -m venv .venv
source .venv/bin/activate
uv run python -m src.main