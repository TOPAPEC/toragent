#!/bin/bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Verify installations
pip list

# Keep terminal open
echo "Environment is ready. Virtual environment is activated."
