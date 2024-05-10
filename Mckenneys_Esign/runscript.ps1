$currentDirectory = (Get-Location).Path
Set-Location -Path $currentDirectory
cd $currentDirectory
python Mckenneys_Esign\jwt_console.py