@echo off
REM Quick launcher for the Flask web app on Windows.
REM Usage:  scripts\run.bat

pushd "%~dp0\..\gui"

if not exist "..\models\best_model.pth" (
    echo X  Model weights not found at models\best_model.pth
    echo    Train the model via notebooks\03_training.ipynb first,
    echo    or place a pre-trained .pth file at that path.
    popd
    exit /b 1
)

echo Starting Australian Raptor CNN on http://localhost:5000
python app.py

popd
