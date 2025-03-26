# Ask for python version
echo "Enter python version (e.g. 3.12):"
read python_version

# Create virtual environment with the specified python version
python$python_version -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip$python_version install -r requirements.txt

# Run the project
python$python_version run.py

# Deactivate virtual environment
deactivate
