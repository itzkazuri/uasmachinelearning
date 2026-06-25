@echo off
setlocal EnableDelayedExpansion
title Cek GPU NVIDIA — Klasifikasi Buah

echo ============================================================
echo   CEK GPU NVIDIA — Klasifikasi Buah
echo ============================================================
echo.

REM ── 1. Cek nvidia-smi ────────────────────────────────────────
echo [1/3] Mengecek driver NVIDIA (nvidia-smi)...
echo ------------------------------------------------------------
where nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo [TIDAK DITEMUKAN] nvidia-smi tidak ada di PATH.
    echo   - Pastikan driver NVIDIA sudah terinstall
    echo   - Download: https://www.nvidia.com/Download/index.aspx
) else (
    nvidia-smi
)

echo.
echo ------------------------------------------------------------
echo [2/3] Mengecek CUDA via nvcc (opsional)...
echo ------------------------------------------------------------
where nvcc >nul 2>&1
if errorlevel 1 (
    echo [INFO] nvcc tidak ditemukan ^(CUDA Toolkit tidak wajib jika
    echo        pakai tensorflow[and-cuda] yang sudah include CUDA^).
) else (
    nvcc --version
)

echo.
echo ------------------------------------------------------------
echo [3/3] Mengecek TensorFlow GPU via venv...
echo ------------------------------------------------------------

if not exist ".venv\Scripts\python.exe" (
    echo [PERINGATAN] Virtual environment belum dibuat.
    echo              Jalankan setup_venv.bat terlebih dahulu.
    echo.
    goto :summary
)

.venv\Scripts\python.exe -c ^
"import tensorflow as tf; ^
print('TensorFlow versi :', tf.__version__); ^
gpus = tf.config.list_physical_devices('GPU'); ^
print('GPU terdeteksi   :', gpus if gpus else 'TIDAK ADA'); ^
print(); ^
[print(f'  [{i}] {g.name}  —  {g.device_type}') for i,g in enumerate(gpus)] if gpus else print('  Tidak ada GPU yang terdeteksi oleh TensorFlow.'); ^
print(); ^
print('Status: OK — Siap training GPU!' if gpus else 'Status: WARNING — Training akan menggunakan CPU.')"

:summary
echo.
echo ============================================================
echo   SELESAI. Tutup window ini atau tekan tombol apapun.
echo ============================================================
echo.
pause
endlocal
