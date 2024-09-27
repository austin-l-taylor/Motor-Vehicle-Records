$currentDirectory = (Get-Location).Path
Set-Location -Path $currentDirectory

# Create a virtual environment and install the required packages
python -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt

python Mckenneys_Esign\jwt_console.py

# Deactivate the virtual environment
deactivate