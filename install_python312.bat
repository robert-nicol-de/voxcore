@echo off
REM Request admin privileges
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting administrator privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set params = %*:"=""
    echo UAC.ShellExecute "cmd.exe", "/c %~s0 %params%", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
cls
echo ========================================
echo VoxQuery - Python 3.12 Installation
echo ========================================
echo.

REM Step 1: Download Python 3.12
echo [1/4] Downloading Python 3.12...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe' -OutFile '%TEMP%\python-3.12.7-amd64.exe' -UseBasicParsing}"
if %errorlevel% neq 0 (
    echo ERROR - Download failed
    pause
    exit /b 1
)
echo OK - Download complete!
echo.

REM Step 2: Uninstall Python 3.14
echo [2/4] Uninstalling Python 3.14...
wmic product where name="Python 3.14" call uninstall /nointeractive >nul 2>&1
if %errorlevel% equ 0 (
    echo OK - Python 3.14 uninstalled!
    timeout /t 3 /nobreak
) else (
    echo Python 3.14 not found (already uninstalled)
)
echo.

REM Step 3: Install Python 3.12
echo [3/4] Installing Python 3.12...
echo This may take 2-3 minutes...
"%TEMP%\python-3.12.7-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
if %errorlevel% neq 0 (
    echo ERROR - Installation failed
    pause
    exit /b 1
)
echo OK - Python 3.12 installed!
timeout /t 3 /nobreak
echo.

REM Step 4: Reinstall packages
echo [4/4] Reinstalling VoxQuery packages...
echo This may take 5-10 minutes...
python -m pip install --upgrade pip --quiet
python -m pip install -r backend/requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ERROR - Package installation failed
    pause
    exit /b 1
)
echo OK - All packages installed!
echo.

REM Cleanup
del "%TEMP%\python-3.12.7-amd64.exe" /q >nul 2>&1

echo ========================================
echo OK - Installation Complete!
echo ========================================
echo.
echo You can now use Snowflake connectivity!
echo.
echo Next steps:
echo 1. Restart your terminal/PowerShell
echo 2. Run: python backend/main.py
echo 3. Connect to Snowflake in VoxQuery
echo.
pause
