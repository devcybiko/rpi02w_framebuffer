#!/bin/bash -v
# python3 -m venv .venv
source .venv/bin/activate
# pip install -r requirements.txt
cd src/clib
python setup.py build_ext --inplace
python3 -m src.main