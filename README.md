# 🍎 Klasifikasi Buah — Sistem Deteksi Kesegaran Buah Berbasis Deep Learning

> **UAS Machine Learning** — Sistem klasifikasi buah otomatis menggunakan Transfer Learning (MobileNetV2) yang mampu mendeteksi jenis buah sekaligus kondisinya (segar/busuk) secara real-time.

---

## 📌 Tentang Project

Project ini adalah sistem kecerdasan buatan untuk mengklasifikasikan buah berdasarkan gambar. Sistem mampu:
- Mengenali **jenis buah** (Apel, Pisang, Jeruk)
- Mendeteksi **kondisi buah** (Segar / Busuk)
- Memberikan **persentase kebusukan** secara otomatis
- Melakukan klasifikasi via **upload gambar**, **GUI desktop**, maupun **kamera real-time**

---

## 📂 Dataset

**Nama:** Fruits Fresh and Rotten for Classification
**Sumber:** Kaggle — oleh Sriram R

🔗 [https://www.kaggle.com/datasets/sriramr/fruits-fresh-and-rotten-for-classification](https://www.kaggle.com/datasets/sriramr/fruits-fresh-and-rotten-for-classification)

| Keterangan | Jumlah |
|---|---|
| Total gambar | ± 13.599 gambar |
| Data Training (80%) | ± 10.879 gambar |
| Data Validasi (20%) | ± 2.720 gambar |
| Jumlah Kelas | 6 kelas |

**Kelas yang tersedia:**

| Label | Keterangan |
|---|---|
| `freshapples` | Apel Segar |
| `freshbanana` | Pisang Segar |
| `freshoranges` | Jeruk Segar |
| `rottenapples` | Apel Busuk |
| `rottenbanana` | Pisang Busuk |
| `rottenoranges` | Jeruk Busuk |

> ⚠️ Dataset **tidak di-commit** ke repository (di-ignore via `.gitignore`).
> Download dari link di atas, lalu ekstrak ke folder `Dataset/` di root project.

```
klasifikasi buah/
└── Dataset/
    ├── freshapples/
    ├── freshbanana/
    ├── freshoranges/
    ├── rottenapples/
    ├── rottenbanana/
    └── rottenoranges/
```

---

## 🤖 Model yang Digunakan

**Metode:** Transfer Learning
**Arsitektur:** MobileNetV2 (pra-latih dengan ImageNet)

```
Input (224x224x3)
      ↓
MobileNetV2 — bobot dibekukan (trainable=False)
      ↓
GlobalAveragePooling2D
      ↓
Dense(128, relu)
      ↓
Dropout(0.2)
      ↓
Dense(6, softmax)  ←  output 6 kelas
```

**Konfigurasi Training:**

| Parameter | Nilai |
|---|---|
| Optimizer | Adam |
| Loss Function | Categorical Crossentropy |
| Epochs | 10 |
| Batch Size | 32 |
| Validation Split | 20% |

**Data Augmentation** diterapkan untuk mencegah overfitting:
rotasi, zoom, horizontal flip, shift, dan shear.

---

## 📊 Hasil dan Analisis

- Model berhasil dilatih selama **10 epoch** dengan Transfer Learning MobileNetV2
- Karena base model dibekukan, training hanya mengoptimalkan lapisan Dense baru → **lebih cepat dan stabil**
- **Data Augmentation** membuat model lebih general terhadap variasi gambar baru
- **Dropout 0.2** efektif mencegah overfitting
- Klasifikasi **real-time via kamera** berjalan lancar dengan bantuan:
  - Color Segmentation (HSV) untuk mendeteksi area buah
  - Haar Cascade untuk mengecualikan wajah manusia dari deteksi

**Contoh output prediksi:**
```json
{
  "prediction": "freshapples",
  "confidence": 0.98,
  "rotten_percentage": 1.2,
  "other_similarities": {
    "freshapples": 98.0,
    "rottenapples": 1.2,
    "freshoranges": 0.5,
    "...": "..."
  }
}
```

> 📄 Laporan lengkap tersedia di file [`uas.txt`](./uas.txt)

---

## 🌱 Kontribusi pada Kehidupan Sehari-hari

| Kontribusi | Dampak |
|---|---|
| **Mengurangi food waste** | Membantu memilah buah layak konsumsi dari yang busuk |
| **Membantu petani & pedagang** | Sortir buah otomatis lebih cepat dari proses manual |
| **Keamanan pangan** | Mencegah konsumsi buah busuk yang membahayakan kesehatan |
| **Potensi industri** | Bisa diintegrasikan ke conveyor belt sortir di gudang/supermarket |
| **Edukasi AI** | Membuktikan AI bisa diaplikasikan pada masalah sehari-hari yang nyata |

---

## 🛠️ Tech Stack

| Komponen | Teknologi |
|---|---|
| Deep Learning | TensorFlow / Keras |
| Arsitektur Model | MobileNetV2 (Transfer Learning) |
| Computer Vision | OpenCV |
| Backend API | FastAPI + Uvicorn |
| Protokol Real-time | WebSocket |
| Frontend Web | Vite + React (TypeScript) |
| GUI Desktop | GTK 4 + Adwaita (Linux) |
| Bahasa | Python 3.11 / 3.12 |

---

## ⚙️ Setup & Menjalankan Project

### 1. Setup Virtual Environment

```bash
chmod +x setup_venv.sh
./setup_venv.sh
source .venv/bin/activate
```

Jika Python 3.11/3.12 tidak ada di `PATH`:
```bash
PYTHON_BIN=/path/to/python3.12 ./setup_venv.sh
```

### 2. Cek GPU (Opsional)

```bash
nvidia-smi
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

### 3. Jalankan Program

```bash
python main.py
```

Menu yang tersedia:
- `1` → Training model (10 epoch)
- `2` → Jalankan API + Frontend Web
- `3` → Buka GUI Desktop (GTK 4)
- `4` → Keluar

---

## 📦 Paket Utama

- `tensorflow[and-cuda]` — training GPU dan MobileNetV2
- `fastapi`, `uvicorn`, `python-multipart` — API upload gambar
- `pillow`, `opencv-python`, `scikit-learn`, `pandas`, `matplotlib`, `tqdm` — pipeline klasifikasi

