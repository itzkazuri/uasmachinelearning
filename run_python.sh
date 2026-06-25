#!/usr/bin/env bash
# run_python.sh - Helper untuk menjalankan script dengan GPU aktif

# 1. Cari path library NVIDIA dari venv
SITE_PACKAGES=$(.venv/bin/python -c "import site; print(site.getsitepackages()[0])")
NVIDIA_LIBS=$(find "$SITE_PACKAGES/nvidia" -type d -name "lib" 2>/dev/null | tr '\n' ':')

# 2. Set LD_LIBRARY_PATH
export LD_LIBRARY_PATH="${NVIDIA_LIBS}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"

# 3. Jalankan python dari venv
exec .venv/bin/python "$@"
