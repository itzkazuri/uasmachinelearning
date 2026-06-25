#!/usr/bin/env bash

set -euo pipefail

if [[ -n "${PYTHON_BIN:-}" ]]; then
  python_bin="$PYTHON_BIN"
else
  python_bin=""
  for candidate in python3.11 python3.12; do
    if command -v "$candidate" >/dev/null 2>&1; then
      python_bin="$candidate"
      break
    fi
  done
fi

if [[ -z "$python_bin" ]]; then
  cat <<'EOF'
Python 3.11 atau 3.12 belum ditemukan.

Install salah satu versi itu dulu, lalu jalankan lagi:
  ./setup_venv.sh

Atau tentukan manual:
  PYTHON_BIN=/path/to/python3.11 ./setup_venv.sh
EOF
  exit 1
fi

python_version="$("$python_bin" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
case "$python_version" in
  3.11|3.12) ;;
  *)
    echo "Interpreter $python_bin memakai Python $python_version."
    echo "Gunakan Python 3.11 atau 3.12 untuk TensorFlow GPU."
    exit 1
    ;;
esac

echo "Menggunakan $python_bin (versi $python_version)"

# Hapus venv lama jika ada untuk memastikan bersih
if [ -d ".venv" ]; then
    echo "Membersihkan venv lama..."
    rm -rf .venv
fi

"$python_bin" -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

# Fix untuk TensorFlow GPU detection (LD_LIBRARY_PATH untuk pip-installed CUDA)
# Ini mencari library NVIDIA yang diinstall lewat pip agar terbaca oleh TensorFlow
SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
NVIDIA_LIBS=$(find "$SITE_PACKAGES/nvidia" -type d -name "lib" 2>/dev/null | tr '\n' ':')
export LD_LIBRARY_PATH="${NVIDIA_LIBS}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"

echo "----------------------------------------------------"
echo "Verifikasi TensorFlow..."
python - <<'PY'
import tensorflow as tf
import os

print("TensorFlow:", tf.__version__)
gpus = tf.config.list_physical_devices("GPU")
print("GPU terdeteksi:", gpus)

if not gpus:
    print("\nDEBUG INFO:")
    print("LD_LIBRARY_PATH:", os.environ.get("LD_LIBRARY_PATH"))
    raise SystemExit("TensorFlow belum mendeteksi GPU. Cek driver NVIDIA dan output nvidia-smi.")
PY

echo "----------------------------------------------------"
echo "Setup Selesai!"
echo "PENTING: Agar GPU terdeteksi saat menjalankan aplikasi, gunakan command berikut:"
echo ""
echo "  export LD_LIBRARY_PATH=\"\$(find \$(pwd)/.venv -type d -name lib | grep nvidia | tr '\\n' ':')\${LD_LIBRARY_PATH:+:\$LD_LIBRARY_PATH}\""
echo "  source .venv/bin/activate"
echo ""
echo "Atau jalankan script Anda lewat helper (misal: ./run_app.sh)"
