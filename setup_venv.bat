@echo off
setlocal EnableDelayedExpansion
title Setup Virtual Environment — Klasifikasi Buah

echo ============================================================
echo   SETUP VIRTUAL ENVIRONMENT — Klasifikasi Buah
echo   Untuk TensorFlow GPU, dibutuhkan Python 3.11 atau 3.12
echo ============================================================
echo.

REM ── 1. Tentukan python binary ────────────────────────────────
set "PYTHON_BIN="

REM Cek argumen pertama (misal: setup_venv.bat C:\Python311\python.exe)
if not "%~1"=="" (
    set "PYTHON_BIN=%~1"
    echo [INFO] Menggunakan Python dari argumen: !PYTHON_BIN!
    goto :check_version
)

REM Auto-detect python3.11 atau python3.12
for %%C in (py.exe python3.11.exe python3.12.exe python3.11 python3.12) do (
    where %%C >nul 2>&1
    if !errorlevel!==0 (
        for /f "delims=" %%P in ('where %%C 2^>nul') do (
            set "PYTHON_BIN=%%P"
            goto :check_version
        )
    )
)

REM Fallback: coba lewat py launcher (Windows Python Launcher)
for %%V in (3.11 3.12) do (
    py -%%V --version >nul 2>&1
    if !errorlevel!==0 (
        set "PYTHON_BIN=py -%%V"
        goto :check_version
    )
)

echo [ERROR] Python 3.11 atau 3.12 tidak ditemukan di PATH.
echo.
echo Solusi:
echo   1. Install Python 3.11 atau 3.12 dari https://www.python.org/downloads/
echo   2. Atau tentukan path manual saat menjalankan script ini:
echo      setup_venv.bat C:\Python311\python.exe
echo.
pause
exit /b 1

:check_version
REM ── 2. Validasi versi Python ──────────────────────────────────
for /f "delims=" %%V in ('!PYTHON_BIN! -c "import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}\")" 2^>nul') do (
    set "PY_VER=%%V"
)

if "!PY_VER!"=="3.11" goto :version_ok
if "!PY_VER!"=="3.12" goto :version_ok

echo [ERROR] Python !PY_VER! tidak didukung untuk TensorFlow GPU.
echo         Gunakan Python 3.11 atau 3.12.
pause
exit /b 1

:version_ok
echo [OK] Menggunakan Python !PY_VER! — !PYTHON_BIN!
echo.

REM ── 3. Hapus venv lama ───────────────────────────────────────
if exist ".venv" (
    echo [INFO] Membersihkan venv lama...
    rmdir /s /q ".venv"
)

REM ── 4. Buat venv baru ────────────────────────────────────────
echo [INFO] Membuat virtual environment baru...
!PYTHON_BIN! -m venv .venv
if errorlevel 1 (
    echo [ERROR] Gagal membuat virtual environment.
    pause
    exit /b 1
)

REM ── 5. Upgrade pip dan install requirements ──────────────────
echo.
echo [INFO] Mengupgrade pip, setuptools, wheel...
.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel

echo.
echo [INFO] Menginstall requirements.txt...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Gagal menginstall requirements. Cek requirements.txt.
    pause
    exit /b 1
)

REM ── 6. Verifikasi TensorFlow + GPU ───────────────────────────
echo.
echo ------------------------------------------------------------
echo [INFO] Verifikasi TensorFlow dan GPU...
echo ------------------------------------------------------------
.venv\Scripts\python.exe -c ^
"import tensorflow as tf; ^
gpus = tf.config.list_physical_devices('GPU'); ^
print('TensorFlow:', tf.__version__); ^
print('GPU terdeteksi:', gpus); ^
exit(0 if gpus else 1)"

if errorlevel 1 (
    echo.
    echo [PERINGATAN] TensorFlow belum mendeteksi GPU.
    echo   - Pastikan driver NVIDIA sudah terinstall
    echo   - Jalankan: nvidia-smi  (di Command Prompt)
    echo   - TensorFlow GPU di Windows membutuhkan CUDA Toolkit ^& cuDNN
    echo     atau gunakan tensorflow[and-cuda] yang sudah include library CUDA
    echo.
) else (
    echo.
    echo [SUKSES] GPU terdeteksi! TensorFlow siap digunakan dengan GPU.
)

REM ── 7. Selesai ───────────────────────────────────────────────
echo.
echo ============================================================
echo   Setup Selesai!
echo   Aktifkan venv dengan perintah:
echo     .venv\Scripts\activate
echo   Lalu jalankan program:
echo     python main.py
echo   Atau gunakan helper script:
echo     run_python.bat main.py
echo ============================================================
echo.
pause
endlocal
