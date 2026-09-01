@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "REPO=https://github.com/jiwonida-dotcom/Manual_All.git"
set "BRANCH=main"

echo ============================================
echo  Manual_All  push
echo ============================================
echo.

where git >nul 2>&1
if errorlevel 1 (
  echo [ERROR] git not found. Install Git for Windows first.
  goto :fail
)

echo [1/7] repository
if not exist ".git" (
  git init
  if errorlevel 1 goto :fail
  echo       initialized
) else (
  echo       existing
)

echo [2/7] stale lock
if exist ".git\index.lock" (
  del /f /q ".git\index.lock" >nul 2>&1
  echo       index.lock removed
) else (
  echo       none
)

echo [3/7] remote
git remote get-url origin >nul 2>&1
if errorlevel 1 (
  git remote add origin "%REPO%"
) else (
  git remote set-url origin "%REPO%"
)
if errorlevel 1 goto :fail
for /f "delims=" %%u in ('git remote get-url origin') do echo       %%u

echo [4/7] branch
git branch -M %BRANCH% >nul 2>&1

echo [5/7] stage
git add -A
if errorlevel 1 goto :fail

set "MSG=%*"
if "%MSG%"=="" set "MSG=update: %DATE% %TIME%"

echo [6/7] commit
git diff --cached --quiet
if errorlevel 1 (
  git commit -m "%MSG%"
  if errorlevel 1 goto :fail
) else (
  echo       no changes to commit
)

echo [7/7] push
git push -u origin %BRANCH%
if errorlevel 1 goto :fail

echo.
echo ---- DONE ----
echo repo  : https://github.com/jiwonida-dotcom/Manual_All
echo pages : https://jiwonida-dotcom.github.io/Manual_All/
echo.
echo * GitHub Pages : Settings ^> Pages ^> Source = main / docs
echo * index.html is served from both root and /docs
echo.
pause
exit /b 0

:fail
echo.
echo ---- FAILED ---- see messages above
echo.
pause
exit /b 1
