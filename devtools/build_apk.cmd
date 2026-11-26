@echo off
REM Windows shim: keep the machine execution policy untouched.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_apk.ps1" %*
