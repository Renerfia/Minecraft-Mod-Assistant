@echo off
echo Installing required packages...
pip install customtkinter pyinstaller

echo.
echo Building the Mod Agent Desktop Application...
echo This might take a minute...
pyinstaller --name "ModAssistantApp" --onefile --windowed app.py

echo.
echo Complete! 
echo Your app is built and located in the 'dist' folder.
echo You can share 'dist\ModAssistantApp.exe' with your users!
pause
