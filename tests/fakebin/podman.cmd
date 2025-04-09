@echo off
if "%1"=="machine" (
    if "%2"=="init" (
        REM Simulate a response for podman machine init
        echo error >&2
        exit /B 1
    )
)

if "%1"=="machine" (
    if "%2"=="start" (
        REM Simulate a response for podman machine start
        echo error >&2
        exit /B 1
    )
)