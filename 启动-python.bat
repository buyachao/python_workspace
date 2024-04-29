@echo off
setlocal enabledelayedexpansion

start python D:\Pro\python_workspace\testSerial.py

:: 设置可变的 EXE_NAME
set "EXE_NAME_VAR=COM"

:: 可选取值 4 6 8 10 12 14 16 18
set "PATHS=4 6 8 10 12 14 16 18"

for %%p in (%PATHS%) do (
    set "PROGRAM_PATH=D:\Pro\COM%%p\"
    set "EXE_NAME=!EXE_NAME_VAR!%%p.exe"
    if exist "!PROGRAM_PATH!" (
        echo execpro !PROGRAM_PATH!!EXE_NAME!...
		timeout /t 1 >nul
		::启动新窗体
		::start cmd /c !PROGRAM_PATH!!EXE_NAME!
		::后台运行
        start /B !PROGRAM_PATH!!EXE_NAME!
    ) else (
        echo can not find !EXE_NAME! in D:\Pro\COM%%p\
    )
)

:end
:pause