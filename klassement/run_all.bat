@echo on
setlocal EnableExtensions

REM Ga altijd naar de map waar dit .bat-bestand staat
cd /d "%~dp0"

set "PY_EXE=python"

REM Optioneel: argumenten (run_all.bat 2026 Ja)
set "YEAR=%~1"
set "PDF=%~2"

if not defined YEAR set /p YEAR=Jaar (bv. 2026):
if not defined PDF set /p PDF=PDF's genereren? (Ja/Nee):

if "%YEAR%"=="" set "YEAR=2026"
if /I "%PDF%"=="" set "PDF=Ja"

echo === Gebruik Python: %PY_EXE%
echo Jaar=%YEAR%  PDF=%PDF%
echo.

REM 1) CSV exporteren
"%PY_EXE%" scores_ophalen.py --jaar %YEAR%
if errorlevel 1 (
  echo [FOUT] scores_ophalen.py mislukte.
  goto :END
)

echo ---- CSV's in data\%YEAR% ----
dir /b "data\%YEAR%\*.csv"
echo.

REM 2) HTML (+ optioneel PDF) genereren
(
  echo %YEAR%
  echo %PDF%
) | "%PY_EXE%" main.py
if errorlevel 1 (
  echo [FOUT] main.py mislukte.
  goto :END
)

echo.
echo === Klaar. Open: output\%YEAR%\html\
echo (PDF's in output\%YEAR%\pdf\ als gekozen)

:END
pause
endlocal
