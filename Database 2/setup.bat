@echo off
"C:\Program Files\7-Zip\7z.exe" x -y "%CD%\site-packages.zip"
SET src_folder=%CD%\site-packages
SET tar_folder=%CD%
for /f %%a IN ('dir "%src_folder%" /b') do move "%src_folder%\%%a" "%tar_folder%\"
md C:\oracle\instantclient_12_2\vc14
"C:\Program Files\7-Zip\7z.exe" x -y "%CD%\instantclient-basic-windows.x64-12.2.0.1.0.zip"
SET src_folder=%CD%\instantclient_12_2
SET tar_folder=C:\oracle\instantclient_12_2
for /f %%a IN ('dir "%src_folder%" /b') do move "%src_folder%\%%a" "%tar_folder%\"
rmdir /s /q site-packages
rmdir /s /q instantclient_12_2
start %CD%\set_path_env_shc
pause