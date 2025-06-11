#!/bin/bash

echo "Installing OpenBB Terminal..."

# Create a virtual environment
python3 -m venv openbb_env

# Activate virtual environment
source openbb_env/bin/activate

# Install required packages
pip install --upgrade pip
pip install wheel
pip install poetry

# Install OpenBB using pip
pip install openbb

# Create a startup script
echo '#!/bin/bash
source openbb_env/bin/activate
python3 -m openbb' > start_openbb.sh

# Make startup script executable
chmod +x start_openbb.sh

echo "Installation complete! Run ./start_openbb.sh to start OpenBB Terminal" 