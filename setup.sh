#!/bin/bash

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Clean install dependencies
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Run verification script
python verify.py

# Print next steps
echo -e "\nSetup complete! Next steps:"
echo "1. Run 'python train.py' to fine-tune the model"
echo "2. After training, test the agent with:"
echo "   python agent.py \"Create a new Git branch\""\

