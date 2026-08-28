@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "REPO=https://github.com/jiwonida-dotcom/202608_GoogleSheet.git"
set "BRANCH=main"

echo ============================================
echo  202608_GoogleSheet  push
echo ============================================
echo.

where git >nul 2>&1
if errorlevel 1 (
  echo [ERROR] git not found. Install Git for Windows first.
  goto :fail
)

echo [1/6] repository
if not exist ".git" (
  git init
  if errorlevel 1 goto :fail
  echo       initialized
) else (
  echo       existing
)

echo [2/6] remote
git remote get-url origin >nul 2>&1
if errorlevel 1 (
  git remote add origin "%REPO%"
) else (
  git remote set-url origin "%REPO%"
)
if errorlevel 1 goto :fail

echo [3/6] branch
git branch -M %BRANCH% >nul 2>&1

echo [4/6] stage
git add -A
if errorlevel 1 goto :fail

set "MSG=%*"
if "%MSG%"=="" set "MSG=update: %DATE% %TIME%"

echo [5/6] commit
git diff --cached --quiet
if errorlevel 1 (
  git commit -m "%MSG%"
  if errorlevel 1 goto :fail
) else (
  echo       no changes to commit
)

echo [6/6] push
git push -u origin %BRANCH%
if errorlevel 1 goto :fail

echo.
echo ---- DONE ----
echo repo  : https://github.com/jiwonida-dotcom/202608_GoogleSheet
echo pages : https://jiwonida-dotcom.github.io/202608_GoogleSheet/
echo.
echo * GitHub Pages : Settings ^> Pages ^> Source = main / (root)
echo.
pause
exit /b 0

:fail
echo.
echo ---- FAILED ---- see messages above
echo.
pause
exit /b 1
