# Klasifikasi Buah

Environment ini disiapkan untuk training klasifikasi gambar dengan GPU NVIDIA, MobileNetV2 dari TensorFlow/Keras, dan FastAPI untuk inference API.

## Dataset

Dataset yang digunakan: **Fruits Fresh and Rotten for Classification** dari Kaggle.

🔗 [https://www.kaggle.com/datasets/sriramr/fruits-fresh-and-rotten-for-classification](https://www.kaggle.com/datasets/sriramr/fruits-fresh-and-rotten-for-classification)

> **Catatan:** Dataset **tidak di-commit** ke repository (sudah di-ignore via `.gitignore`).
> Download manual dari link di atas, lalu ekstrak ke folder `Dataset/` di root project.

```
klasifikasi buah/
└── Dataset/
    ├── train/
    │   ├── freshapples/
    │   ├── rottenapples/
    │   └── ...
    └── test/
        ├── freshapples/
        ├── rottenapples/
        └── ...
```

## Setup venv

Python default kamu adalah 3.14.5. Untuk TensorFlow GPU, pakai Python 3.11 atau 3.12.

```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

Kalau Python 3.11/3.12 tidak ada di `PATH`:

```bash
PYTHON_BIN=/path/to/python3.12 ./setup_venv.sh
```

Aktivasi venv setelah berhasil:

```bash
source .venv/bin/activate
```

## Cek GPU

```bash
nvidia-smi
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

## Paket utama

- `tensorflow[and-cuda]` untuk training GPU dan MobileNetV2.
- `fastapi`, `uvicorn`, `python-multipart` untuk API upload gambar.
- `pillow`, `opencv-python`, `scikit-learn`, `pandas`, `matplotlib`, `tqdm` untuk pipeline klasifikasi gambar.
