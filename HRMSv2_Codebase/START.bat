@echo off
SET cmd1=python %CD%\codebase.py %*
start cmd /k "activate hrms & %cmd1% & exit"