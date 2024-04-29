@echo off
setlocal enabledelayedexpansion

:: 设置可变的 EXE_NAME
set "EXE_NAME_VAR=COM"

:: 可选取值 4、6、8、10
set "PATHS=4 6 8 10"

for %%p in (%PATHS%) do (
    set "PROGRAM_PATH=D:\Pro\COM%%p\"
    set "EXE_NAME=!EXE_NAME_VAR!%%p.exe"
    if exist "!PROGRAM_PATH!" (
        echo execpro !PROGRAM_PATH!!EXE_NAME!...
		timeout /t 2 >nul
		start cmd /c !PROGRAM_PATH!!EXE_NAME!
    ) else (
        echo can not find !EXE_NAME! in D:\Pro\COM%%p\
    )
)

:end
:pause