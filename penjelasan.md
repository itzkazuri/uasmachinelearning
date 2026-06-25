Penjelasan Program Klasifikasi Buah Berbasis Deep Learning

Program ini adalah sistem klasifikasi buah yang menggunakan kecerdasan buatan, khususnya teknik deep learning dengan pendekatan Transfer Learning. Sistem ini mampu mengenali jenis buah dari sebuah gambar serta memperkirakan tingkat kebusukan buah tersebut. Program dibangun menggunakan bahasa Python dan terdiri dari beberapa bagian utama yang masing-masing memiliki peran berbeda.


METODE YANG DIGUNAKAN

Metode utama yang digunakan dalam proyek ini adalah Transfer Learning dengan arsitektur MobileNetV2. Transfer Learning adalah teknik di mana sebuah model yang sudah dilatih sebelumnya menggunakan dataset sangat besar (dalam hal ini ImageNet yang berisi jutaan gambar dari ribuan kategori) digunakan kembali sebagai fondasi untuk menyelesaikan tugas baru yang lebih spesifik. Teknik ini sangat efisien karena tidak perlu melatih model dari nol, sehingga proses training menjadi lebih cepat dan hasil yang dicapai tetap akurat meskipun dataset yang dimiliki relatif kecil.

MobileNetV2 dipilih karena arsitekturnya yang ringan dan efisien, cocok untuk dijalankan pada komputer biasa tanpa memerlukan GPU yang sangat kuat. Model ini menggunakan teknik depthwise separable convolution yang dapat mengekstrak fitur-fitur visual dari gambar secara efektif dengan beban komputasi yang lebih rendah dibandingkan arsitektur lain seperti VGG16 atau ResNet.

Selain Transfer Learning, program ini juga menerapkan teknik Data Augmentation pada saat proses training. Data augmentation adalah proses memperbanyak variasi data latih secara buatan dengan cara melakukan transformasi acak pada gambar, seperti rotasi, pergeseran posisi, zoom, dan pencerminan horizontal. Tujuannya adalah agar model tidak menghafal gambar latih saja (overfitting), melainkan benar-benar belajar mengenali fitur-fitur penting dari buah sehingga performa pada data baru tetap baik.


BAGIAN 1: PROSES TRAINING MODEL (src/train.py)

File ini berisi seluruh logika untuk melatih model kecerdasan buatan. Proses training terbagi menjadi lima tahap.

Tahap pertama adalah persiapan data. Program membaca gambar-gambar buah dari folder Dataset yang sudah diorganisir per kelas. Setiap gambar diubah ukurannya menjadi 224x224 piksel agar sesuai dengan format masukan MobileNetV2. Nilai piksel gambar yang aslinya berkisar 0 sampai 255 dibagi dengan 255 sehingga menjadi rentang 0 sampai 1, proses ini disebut normalisasi. Data kemudian dibagi secara otomatis dengan rasio 80% untuk data latih dan 20% untuk data validasi menggunakan parameter validation_split. Data augmentation juga diterapkan pada tahap ini dengan parameter seperti rotation_range, zoom_range, dan horizontal_flip.

Tahap kedua adalah pembangunan arsitektur model. MobileNetV2 yang sudah terlatih pada ImageNet diambil seluruh lapisan konvolusionalnya tetapi lapisan terakhirnya dihilangkan (parameter include_top=False). Seluruh bobot lapisan ini kemudian dibekukan (base_model.trainable = False) agar tidak berubah selama training, sehingga hanya lapisan baru yang ditambahkan saja yang akan dipelajari. Di atas lapisan MobileNetV2 tersebut ditambahkan tiga lapisan baru: pertama GlobalAveragePooling2D yang mengubah output konvolusi menjadi sebuah vektor; kedua Dense layer dengan 128 neuron dan fungsi aktivasi ReLU sebagai lapisan tersembunyi; ketiga Dropout layer dengan nilai 0.2 untuk mencegah overfitting dengan cara menonaktifkan secara acak 20% neuron selama training; dan terakhir lapisan output Dense dengan jumlah neuron sesuai jumlah kelas buah yang ada, menggunakan fungsi aktivasi softmax agar outputnya berupa distribusi probabilitas.

Tahap ketiga adalah kompilasi model. Model dikompilasi menggunakan optimizer Adam yang merupakan salah satu optimizer paling populer karena mampu menyesuaikan learning rate secara adaptif. Fungsi loss yang digunakan adalah categorical_crossentropy yang cocok untuk permasalahan klasifikasi multi-kelas. Metrik yang dipantau adalah accuracy.

Tahap keempat adalah proses training itu sendiri. Model dilatih selama 10 epoch, artinya seluruh data latih ditelusuri sebanyak 10 kali. Pada setiap akhir epoch, performa model diuji menggunakan data validasi untuk memantau apakah model mengalami overfitting atau tidak.

Tahap kelima adalah penyimpanan model. Setelah training selesai, model disimpan dalam format .keras dan daftar nama kelas buah disimpan dalam file teks terpisah agar dapat digunakan kembali saat prediksi tanpa perlu training ulang.


BAGIAN 2: PREDIKSI GAMBAR (src/predict.py)

File ini berisi kelas FruitClassifier yang bertanggung jawab atas proses prediksi atau inferensi. Ketika sebuah gambar buah diberikan, kelas ini melakukan serangkaian langkah untuk menghasilkan prediksi.

Pertama, gambar dimuat dan diubah ukurannya menjadi 224x224 piksel, kemudian diubah menjadi array numerik dan dinormalisasi. Sebuah dimensi tambahan ditambahkan di depan array menggunakan np.expand_dims karena model mengharapkan input dalam bentuk batch walaupun hanya satu gambar.

Setelah melewati model, output yang dihasilkan adalah sebuah array berisi angka-angka probabilitas untuk setiap kelas buah. Jumlah seluruh probabilitas ini selalu sama dengan 1 atau 100%. Program kemudian mencari indeks dengan nilai probabilitas tertinggi menggunakan np.argmax sebagai prediksi utama.

Fitur menarik dalam kelas ini adalah perhitungan persentase kebusukan. Program secara otomatis mencari semua kelas yang mengandung kata rotten dalam namanya, lalu menjumlahkan semua probabilitasnya. Hasil penjumlahan ini diinterpretasikan sebagai estimasi tingkat kebusukan buah dalam bentuk persentase. Selain itu, program juga mengembalikan daftar kemiripan dengan seluruh kelas buah yang diurutkan dari probabilitas tertinggi ke terendah.

Kelas ini mendukung dua metode masukan gambar: prediksi dari path file gambar di disk, dan prediksi langsung dari data bytes gambar yang berguna untuk integrasi dengan server API secara real-time.


BAGIAN 3: SERVER API (api/server.py)

File ini membangun sebuah server API menggunakan framework FastAPI. Server ini berfungsi sebagai jembatan antara model AI dan antarmuka pengguna berbasis web.

Server menyediakan dua endpoint. Pertama adalah endpoint HTTP POST di alamat /predict yang menerima upload file gambar dari pengguna melalui form, menyimpannya sementara di disk, menjalankan prediksi, lalu mengembalikan hasil dalam format JSON. File sementara langsung dihapus setelah prediksi selesai untuk menjaga kebersihan penyimpanan.

Kedua adalah endpoint WebSocket di alamat /ws/predict yang memungkinkan komunikasi dua arah secara terus-menerus antara klien dan server. Endpoint ini dirancang khusus untuk mendukung klasifikasi gambar secara real-time, seperti dari kamera langsung. Klien mengirimkan frame gambar dalam bentuk bytes, server langsung memproses dan mengirim kembali hasilnya, dan siklus ini berulang terus menerus selama koneksi masih aktif.


BAGIAN 4: ANTARMUKA GUI DESKTOP (gui/app.py)

File ini membangun antarmuka pengguna grafis berbasis desktop menggunakan library GTK 4 dengan gaya visual Adwaita, yaitu standar antarmuka bawaan GNOME Linux. Program membuat sebuah jendela aplikasi dengan dua halaman yang dapat dipilih melalui tab di bagian atas.

Halaman pertama adalah halaman klasifikasi. Pengguna dapat memilih foto buah dari komputer menggunakan dialog pemilih file. Foto yang dipilih akan ditampilkan sebagai pratinjau dalam jendela. Proses prediksi dijalankan di background thread yang terpisah dari thread antarmuka agar tampilan tidak membeku selama proses berlangsung. Setelah selesai, hasil prediksi berupa nama buah, tingkat kepastian dalam persen, dan estimasi kebusukan ditampilkan dalam daftar yang rapi. Pengguna juga dapat melihat daftar kemiripan dengan buah-buah lain melalui komponen yang bisa dibuka dan ditutup.

Halaman kedua adalah halaman pengelolaan server API. Dari sini pengguna dapat menghidupkan dan mematikan server FastAPI langsung melalui antarmuka grafis tanpa perlu membuka terminal.


BAGIAN 5: KLASIFIKASI REAL-TIME DENGAN KAMERA (gui/realtime_camera.py)

File ini adalah fitur paling canggih dalam proyek ini. Program mengakses kamera webcam secara langsung dan melakukan klasifikasi buah secara real-time, artinya prediksi dilakukan terus menerus tanpa berhenti.

Program menggabungkan dua teknologi computer vision secara bersamaan. Pertama adalah Haar Cascade Classifier bawaan OpenCV untuk mendeteksi wajah manusia di dalam frame kamera. Wajah yang terdeteksi kemudian dikecualikan dari proses tracking buah agar kamera tidak salah mengidentifikasi wajah manusia sebagai buah.

Kedua adalah Color Segmentation berbasis ruang warna HSV. Berbeda dengan ruang warna RGB yang umum digunakan, HSV memisahkan informasi warna dari kecerahan sehingga lebih tahan terhadap perubahan kondisi pencahayaan. Program mendefinisikan rentang warna yang umumnya dimiliki buah seperti merah, kuning, oranye, dan hijau, lalu membuat mask yang hanya mempertahankan area dengan warna tersebut.

Setelah area buah ditemukan menggunakan analisis kontur, program menghitung pusat massa kontur terbesar menggunakan momen citra. Posisi ROI (Region of Interest) berupa kotak seleksi kemudian digerakkan secara halus menuju pusat buah menggunakan teknik exponential smoothing, menghasilkan gerakan kotak yang lembut dan tidak melompat-lompat.

Frame dalam ROI dikirimkan ke server API melalui koneksi WebSocket yang berjalan di thread terpisah. Hasil prediksi diterima kembali dan ditampilkan langsung di atas video menggunakan overlay teks. Seluruh tampilan dirender menggunakan OpenCV dengan kotak berwarna hijau jika tingkat kepastian lebih dari 70 persen dan kuning jika di bawah itu.


BAGIAN 6: PROGRAM UTAMA (main.py)

File ini adalah titik masuk dari keseluruhan program. Ia menyediakan menu sederhana berbasis teks di terminal yang memungkinkan pengguna memilih antara empat opsi: menjalankan training model, menjalankan server API bersama antarmuka web Vite, membuka aplikasi GUI desktop, atau keluar dari program. Program ini juga secara otomatis mendeteksi apakah pengelola paket Bun atau npm yang tersedia di sistem untuk menginstal dependensi frontend.


RINGKASAN TEKNOLOGI YANG DIGUNAKAN

Bahasa pemrograman yang digunakan adalah Python. Untuk deep learning dan pemrosesan gambar digunakan TensorFlow dan Keras. Arsitektur model yang diterapkan adalah MobileNetV2 dengan pendekatan Transfer Learning. Untuk computer vision real-time digunakan OpenCV. Server API dibangun menggunakan FastAPI dengan protokol komunikasi HTTP REST dan WebSocket. Antarmuka desktop menggunakan GTK 4 dan Adwaita. Antarmuka web dibangun menggunakan Vite sebagai build tool frontend. Komunikasi asinkron ditangani menggunakan modul asyncio dan websockets bawaan Python.
