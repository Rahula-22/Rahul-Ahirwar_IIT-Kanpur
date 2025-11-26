@echo off
echo ========================================
echo GitHub Submission Cleanup
echo ========================================
echo.
echo This will remove all unnecessary files for clean submission
echo.
pause

echo Removing debug and test files...
del /q debug_*.py 2>nul
del /q debug_*.txt 2>nul
del /q test_simple.py 2>nul
del /q test_custom.py 2>nul
del /q test_with_url.py 2>nul
del /q create_test_image.py 2>nul
del /q test_*.png 2>nul

echo Removing setup helper scripts...
del /q clean_install.bat 2>nul
del /q final_setup.bat 2>nul
del /q fix_tesseract_path.bat 2>nul
del /q quick_start.bat 2>nul

echo Removing extra documentation...
del /q TESSERACT_FIX.md 2>nul
del /q QUICK_FIX.md 2>nul
del /q FINAL_RUN_INSTRUCTIONS.md 2>nul
del /q START_WITHOUT_TESSERACT.md 2>nul
del /q UPLOAD_TEST_GUIDE.md 2>nul

echo Cleaning temporary files...
del /q temp\* 2>nul
del /q logs\*.log 2>nul

echo Removing preprocessed images...
del /q *_preprocessed.png 2>nul

echo.
echo ✅ Cleanup complete!
echo.
echo Files retained for submission:
echo   - app/ (core application)
echo   - static/ (web UI)
echo   - requirements.txt
echo   - README.md
echo   - SETUP_GUIDE.md
echo   - SUBMISSION_CHECKLIST.md
echo   - test_api.py (assignment testing)
echo   - verify_setup.py
echo   - .env.example
echo   - .gitignore
echo   - Dockerfile
echo.
pause
