@ECHO OFF
SET BASE_FOLDER=C:\Fuzzing
SET PYTHON_EXE=C:\Python27\python.exe

:: What browser do we want to fuzz? ("chrome" | "edge" | "firefox" | "msie")
SET TARGET_BROWSER=edge
:: How many HTML files shall we teach during each loop?
SET NUMBER_OF_FILES=100
:: How long does it take BugId to start the browser and load an HTML file?
SET BROWSER_LOAD_TIMEOUT_IN_SECONDS=30
:: How long does it take the browser to render each HTML file?
SET AVERAGE_PAGE_LOAD_TIME_IN_SECONDS=2

:: Optionally configurable
SET BUGID_FOLDER=%BASE_FOLDER%\BugId
SET DOMATO_FOLDER=%BASE_FOLDER%\domato-master
SET TESTS_FOLDER=%BASE_FOLDER%\Tests
SET REPORT_FOLDER=%BASE_FOLDER%\Report
SET RESULT_FOLDER=%BASE_FOLDER%\Results
:: Store our results in a folder named after the target:
IF NOT EXIST "%RESULT_FOLDER%\%TARGET_BROWSER%" MKDIR "%RESULT_FOLDER%\%TARGET_BROWSER%"

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Repeatedly generate tests and run them in the browser.
:LOOP
  CALL :GENERATE
  IF ERRORLEVEL 1 EXIT /B 1
  CALL :TEST
  IF ERRORLEVEL 1 EXIT /B 1
  GOTO :LOOP

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Generate test HTML files
:GENERATE
  REM Delete old files.
  DEL "%TESTS_FOLDER%\fuzz-*.html" /Q >nul 2>nul
  REM Generate new HTML files.
  "%PYTHON_EXE%" "%DOMATO_FOLDER%\generator.py" --output_dir "%TESTS_FOLDER%" --no_of_files %NUMBER_OF_FILES%
  IF ERRORLEVEL 1 EXIT /B 1
  EXIT /B 0

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Run browser in BugId and load test HTML files
:TEST
  REM Delete old report if any.
  IF NOT EXIST "%REPORT_FOLDER%" (
    MKDIR "%REPORT_FOLDER%"
  ) ELSE (
    DEL "%REPORT_FOLDER%\*.html" /Q >nul 2>nul
  )
  REM Guess how long the browser needs to run to process all tests.
  REM This is used by BugId to terminate the browser in case it survives all tests.
  SET /A MAX_BROWSER_RUN_TIME=%BROWSER_LOAD_TIMEOUT_IN_SECONDS% + %AVERAGE_PAGE_LOAD_TIME_IN_SECONDS% * %NUMBER_OF_FILES%
  REM Start browser in BugId...
  "%PYTHON_EXE%" "%BUGID_FOLDER%\BugId.py" "%TARGET_BROWSER%" "--sReportFolderPath=\"%REPORT_FOLDER:\=\\%\"" --nApplicationMaxRunTimeInSeconds=%MAX_BROWSER_RUN_TIME% -- "file://%TESTS_FOLDER%\index.html"

  IF ERRORLEVEL 2 (
    ECHO - ERROR %ERRORLEVEL%.
    REM ERRORLEVEL 2+ means something went wrong.
    ECHO Please fix the issue before continuing...
    EXIT /B 1
  ) ELSE IF NOT ERRORLEVEL 1 (
    EXIT /B 0
  )
  ECHO Crash detected!

  REM Create results sub-folder based on report file name and copy test files
  REM and report.
  FOR %%I IN ("%REPORT_FOLDER%\*.html") DO (
    CALL :COPY_TO_UNIQUE_CRASH_FOLDER "%RESULT_FOLDER%\%%~nxI"
    EXIT /B 0
  )
  ECHO BugId reported finding a crash, but not report file could be found!?
  EXIT /B 1

:COPY_TO_UNIQUE_CRASH_FOLDER
  SET REPORT_FILE=%~nx1
  REM We want to remove the ".html" extension from the report file name to get
  REM a unique folder name:
  SET UNIQUE_CRASH_FOLDER=%RESULT_FOLDER%\%TARGET_BROWSER%\%REPORT_FILE:~0,-5%
  IF EXIST "%UNIQUE_CRASH_FOLDER%" (
    ECHO Repro and report already saved after previous test detected the same issue.
    EXIT /B 0
  )
  ECHO Copying report and repro to %UNIQUE_CRASH_FOLDER% folder...
  REM Move report to unique folder
  MKDIR "%UNIQUE_CRASH_FOLDER%"
  MOVE "%REPORT_FOLDER%\%REPORT_FILE%" "%UNIQUE_CRASH_FOLDER%\report.html"
  REM Copy repro
  MKDIR "%UNIQUE_CRASH_FOLDER%\Repro"
  COPY "%TESTS_FOLDER%\*.html" "%UNIQUE_CRASH_FOLDER%\Repro"
  ECHO Report and repro copied to %UNIQUE_CRASH_FOLDER% folder.
  EXIT /B 0
