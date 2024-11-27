# Ensure the script stops on error
$ErrorActionPreference = "Stop"

# Define the path to your virtual environment
$venvPath = ".\.venv"

# Check if the virtual environment exists
if (!(Test-Path -Path $venvPath)) {
    Write-Error "Virtual environment not found at path: $venvPath. Please create it first."
    exit 1
}

# Activate the virtual environment
Write-Output "Activating virtual environment..."
& "$venvPath\Scripts\Activate.ps1"

# Get all subdirectories in the current directory, excluding hidden directories 
$subdirectories = Get-ChildItem -Directory | Where-Object { $_.Name -notmatch "^\." }

foreach ($subdir in $subdirectories) {
    # Construct the path to the requirements.txt file
    $requirementsFile = Join-Path -Path $subdir.FullName -ChildPath "requirements.txt"

    # Check if requirements.txt exists in the subdirectory
    if (Test-Path -Path $requirementsFile) {
        Write-Output "Installing requirements from: $requirementsFile"
        # Run pip install for the requirements.txt file
        pip install -r $requirementsFile
    }
    else {
        Write-Output "No requirements.txt found in: $subdir.FullName"
    }
}

Write-Output "All installations are complete."
