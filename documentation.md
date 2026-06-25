# Dokumentasi Proyek Klasifikasi Buah

Proyek ini adalah sistem klasifikasi buah yang menggunakan Machine Learning untuk mendeteksi kesegaran buah (Segar/Busuk). Sistem ini terdiri dari backend (API), frontend (Web), dan antarmuka grafis (GUI).

## 1. Arsitektur Sistem

- **Model Machine Learning**: Menggunakan MobileNetV2 (TensorFlow/Keras) yang dilatih untuk mengklasifikasikan buah ke dalam beberapa kategori seperti `freshapples`, `freshbanana`, `freshoranges`, `rottenapples`, `rottenbanana`, dan `rottenoranges`.
- **Backend (API)**: Dibangun dengan **FastAPI** untuk melayani request prediksi gambar secara real-time via HTTP POST dan **WebSocket** untuk stream real-time.
- **Frontend (Web)**: Menggunakan **React (TypeScript)** dengan **Vite** dan **Tailwind CSS**.
- **Desktop GUI & Real-time**: Menggunakan Python (GTK4/Adwaita) dan OpenCV untuk klasifikasi real-time melalui kamera.

---

## 2. Struktur Folder

```text
.
├── api/                # Implementasi server FastAPI (HTTP & WebSocket)
├── src/                # Logika inti (Training & Prediksi)
├── models/             # File model (.keras) dan label kelas
├── frontend/           # Proyek React (Vite + TypeScript)
├── gui/                # Aplikasi desktop Python & Real-time Camera
├── Dataset/            # Data gambar untuk training
├── outputs/            # Folder sementara untuk hasil proses
├── requirements.txt    # Dependensi Python
└── setup_venv.sh       # Script otomasi setup environment
```

---

## 3. Panduan Instalasi & Penggunaan

### A. Backend & Machine Learning
Pastikan Anda menggunakan Python 3.11 atau 3.12 untuk kompatibilitas TensorFlow GPU.

1.  **Setup Environment**:
    ```bash
    chmod +x setup_venv.sh
    ./setup_venv.sh
    source .venv/bin/activate
    ```
2.  **Menjalankan API**:
    ```bash
    uvicorn api.server:app --reload
    ```
    API akan berjalan di `http://127.0.0.1:8000`. WebSocket tersedia di `ws://127.0.0.1:8000/ws/predict`.
3.  **Training Model**:
    ```bash
    python src/train.py
    ```

### B. Real-time Camera Classification
Untuk menjalankan klasifikasi buah secara langsung menggunakan kamera (metode WebSocket):
```bash
python gui/realtime_camera.py
```

### C. Frontend (Web)
Menggunakan **Bun** untuk manajemen paket yang lebih cepat.

1.  **Instalasi Dependensi**:
    ```bash
    cd frontend
    bun install
    ```
2.  **Menjalankan Mode Pengembangan**:
    ```bash
    bun dev
    ```

### D. GUI Desktop (Legacy)
Untuk menjalankan aplikasi berbasis window:
```bash
python gui/app.py
```

---

## 4. Endpoint API Utama

### `GET /`
Mengecek status API.

### `POST /predict`
Menerima unggahan file gambar (form-data).

**Payload**: `file` (UploadFile/Binary)
**Response**: JSON hasil klasifikasi.

### `WebSocket /ws/predict` (Real-time)
Menerima stream data gambar dalam bentuk bytes secara kontinu dan mengembalikan hasil prediksi secara instan. Metode ini digunakan oleh aplikasi kamera real-time untuk performa tinggi.

**Input**: Image Bytes (Binary)
**Output**: JSON hasil klasifikasi.

---

## 5. Fitur Unggulan
- **Real-time WebSocket Prediction**: Memungkinkan deteksi buah tanpa delay yang signifikan menggunakan stream kamera.
- **Skor Kebusukan (Rotten Percentage)**: Memberikan indikasi tingkat kebusukan.
- **Akselerasi GPU**: Mendukung penggunaan NVIDIA GPU.
- **Multi-Platform**: API, Web, Desktop GUI, dan Real-time Camera.
