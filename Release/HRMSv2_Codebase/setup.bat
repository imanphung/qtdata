@echo off
:: BatchGotAdmin
:-------------------------------------
REM  --> Check for permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
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
    pushd "%CD%"
    CD /D "%~dp0"
:--------------------------------------

md C:\oracle\instantclient_12_2\vc14
"C:\Program Files\WinRAR\WinRAR.exe" x -y "%CD%\instantclient-basic-windows.x64-12.2.0.1.0.zip"
SET src_folder=%CD%\instantclient_12_2
SET tar_folder=C:\oracle\instantclient_12_2
for /f %%a IN ('dir "%src_folder%" /b') do move "%src_folder%\%%a" "%tar_folder%\"
robocopy %~dp0\instantclient_12_2\vc14 C:\oracle\instantclient_12_2\vc14
setx Path "%PATH%;C:\oracle\instantclient_12_2" /M
rd /q/s %src_folder%

"C:\Program Files\WinRAR\WinRAR.exe" x -y "%CD%\packages.zip"
conda create -n hrms python=3.5.2 --y
SET cmd0=pip install cmake==3.18.0
SET cmd1=pip install "%CD%\packages\dlib-19.20.0-cp35-cp35m-win_amd64.whl"
SET cmd2=pip install -r "%CD%\requirements.txt"
SET cmd3=rd /q/s %CD%\packages
start cmd /k "activate hrms & %cmd0% & %cmd1% & %cmd2% & %cmd3% & exit"
