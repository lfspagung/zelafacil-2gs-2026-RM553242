#!/bin/bash
set -e
apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-por
python -m streamlit run mvp_app/app.py --server.port 8000 --server.address 0.0.0.0
