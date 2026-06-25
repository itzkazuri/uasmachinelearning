@echo off
setlocal EnableDelayedExpansion
title Run Python dengan GPU — Klasifikasi Buah

REM ============================================================
REM  run_python.bat
REM  Helper untuk menjalankan script Python dengan venv aktif
REM
REM  Penggunaan:
REM    run_python.bat main.py
REM    run_python.bat src\train.py
REM    run_python.bat -c "import tensorflow as tf; print(tf.__version__)"
REM
REM  Jalankan tanpa argumen untuk langsung jalankan main.py
REM ============================================================

REM ── Cek venv tersedia ────────────────────────────────────────
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment belum dibuat.
    echo         Jalankan dulu: setup_venv.bat
    echo.
    pause
    exit /b 1
)

REM ── Cek package manager yang tersedia ────────────────────────
set "PKG_MANAGER="
for %%P in (bun.cmd bun pnpm.cmd pnpm yarn.cmd yarn npm.cmd npm) do (
    if "!PKG_MANAGER!"=="" (
        where %%P >nul 2>&1
        if !errorlevel!==0 (
            set "PKG_MANAGER=%%P"
        )
    )
)

if not "!PKG_MANAGER!"=="" (
    echo [INFO] Package manager terdeteksi: !PKG_MANAGER!
) else (
    echo [PERINGATAN] Tidak ada package manager (npm/pnpm/yarn/bun) ditemukan.
    echo              Frontend tidak akan bisa dijalankan.
    echo              Install Node.js dari: https://nodejs.org/
)
echo.

REM ── Set PATH agar venv aktif ─────────────────────────────────
set "PATH=%CD%\.venv\Scripts;%PATH%"

REM ── Jalankan argumen yang diberikan, atau default ke main.py ──
if "%~1"=="" (
    echo [INFO] Tidak ada argumen, menjalankan: main.py
    echo.
    .venv\Scripts\python.exe main.py
) else (
    echo [INFO] Menjalankan: .venv\Scripts\python.exe %*
    echo.
    .venv\Scripts\python.exe %*
)

set "EXIT_CODE=!errorlevel!"

echo.
if !EXIT_CODE!==0 (
    echo [SELESAI] Script selesai tanpa error.
) else (
    echo [ERROR] Script keluar dengan kode error: !EXIT_CODE!
)

endlocal
exit /b %EXIT_CODE%
