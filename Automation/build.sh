#!/bin/bash
# Build script for Render deployment
# This script downloads required spaCy models and NLTK data

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Downloading spaCy model (en_core_web_sm)..."
python -m spacy download en_core_web_sm

echo "Downloading NLTK data..."
python -m nltk.downloader words
python -m nltk.downloader stopwords

echo "Build completed successfully!"

