@echo off
echo ========================================
echo CAD Version Manager - Packaging
echo ========================================
echo.

REM Create output directory
if not exist "CAD_Portable" mkdir "CAD_Portable"

REM Copy files
echo Copying files...
copy "backend\dist\cad-backend.exe" "CAD_Portable\" /Y
xcopy "frontend\dist" "CAD_Portable\frontend\dist\" /E /I /Y

REM Create start script
echo @echo off > "CAD_Portable\Start.bat"
echo title CAD Version Manager >> "CAD_Portable\Start.bat"
echo echo Starting CAD Version Manager... >> "CAD_Portable\Start.bat"
echo start "" "cad-backend.exe" >> "CAD_Portable\Start.bat"
echo timeout /t 3 /nobreak ^>nul >> "CAD_Portable\Start.bat"
echo start http://localhost:8000 >> "CAD_Portable\Start.bat"
echo echo. >> "CAD_Portable\Start.bat"
echo echo CAD Version Manager is running! >> "CAD_Portable\Start.bat"
echo echo Close this window to stop the server. >> "CAD_Portable\Start.bat"
echo pause ^>nul >> "CAD_Portable\Start.bat"

echo.
echo ========================================
echo Done! Portable version created in:
echo   CAD_Portable\
echo.
echo To distribute:
echo   1. Zip the CAD_Portable folder
echo   2. User extracts and runs Start.bat
echo ========================================
pause
