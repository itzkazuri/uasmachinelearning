import sys
import os
import subprocess
import shutil
import platform
from src.train import train_model
import uvicorn

# ── Deteksi OS ────────────────────────────────────────────────
IS_WINDOWS = platform.system() == "Windows"

# ── Deteksi package manager frontend ─────────────────────────
def detect_package_manager():
    """Cari package manager yang tersedia: bun, pnpm, yarn, npm (urutan prioritas)."""
    for pm in ["bun", "pnpm", "yarn", "npm"]:
        if shutil.which(pm):
            return pm
    return None

def run_frontend_server():
    """Install node_modules jika belum ada, lalu jalankan dev server Vite."""
    if not os.path.exists("models/fruit_model.keras"):
        print("\nPERINGATAN: Model tidak ditemukan. Silakan pilih menu 1 dulu.")
        return

    pkg_manager = detect_package_manager()
    if pkg_manager is None:
        print("\n[ERROR] Tidak ditemukan package manager (npm/pnpm/yarn/bun).")
        print("  Install salah satu dari:")
        print("    npm  : https://nodejs.org/")
        print("    pnpm : npm install -g pnpm")
        print("    yarn : npm install -g yarn")
        print("    bun  : https://bun.sh/")
        return

    print(f"\n[INFO] Menggunakan package manager: {pkg_manager}")

    # Install node_modules jika belum ada
    if not os.path.exists("frontend/node_modules"):
        print(f"\nnode_modules tidak ditemukan. Menginstal dependensi dengan '{pkg_manager} install'...")
        try:
            subprocess.run([pkg_manager, "install"], cwd="frontend", check=True)
        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] Gagal menginstal dependensi frontend: {e}")
            print(f"  Coba jalankan manual di folder 'frontend': {pkg_manager} install")
            return
        except FileNotFoundError:
            print(f"\n[ERROR] '{pkg_manager}' tidak dapat dieksekusi. Pastikan Node.js sudah terinstall.")
            return

    # Jalankan Vite dev server
    vite_cmd = [pkg_manager, "run", "dev"]
    print(f"\nMemulai Vite Frontend ({' '.join(vite_cmd)})...")
    frontend_process = None
    try:
        frontend_process = subprocess.Popen(vite_cmd, cwd="frontend")

        # Jalankan FastAPI
        print("\nMemulai server FastAPI di http://127.0.0.1:8000")
        uvicorn.run("api.server:app", host="127.0.0.1", port=8000, reload=True)

    except KeyboardInterrupt:
        print("\nMenerima sinyal keluar...")
    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan: {e}")
    finally:
        if frontend_process:
            print("\nMenghentikan Vite Frontend...")
            frontend_process.terminate()
            try:
                frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                frontend_process.kill()
            print("Vite Frontend berhasil dihentikan.")


def main():
    print("=== FRUIT CLASSIFICATION SYSTEM ===")

    if IS_WINDOWS:
        # ── Menu Windows (tanpa Adwaita GUI — GTK4 khusus Linux) ──
        print("1. Training Model (10 Epochs)")
        print("2. Start API & Frontend Server (FastAPI + Vite)")
        print("3. Exit")
        print("\n[INFO] Berjalan di Windows — GUI Desktop (Adwaita/GTK4) tidak tersedia.")

        choice = input("\nPilih menu (1/2/3): ").strip()

        if choice == "1":
            print("\nMemulai proses training...")
            train_model(epochs=10)
        elif choice == "2":
            run_frontend_server()
        elif choice == "3":
            print("Keluar...")
            sys.exit(0)
        else:
            print("Pilihan tidak valid.")

    else:
        # ── Menu Linux/macOS (dengan Adwaita GUI) ─────────────────
        from gui.app import launch_gui

        print("1. Training Model (10 Epochs)")
        print("2. Start API & Frontend Server (FastAPI + Vite)")
        print("3. Launch Adwaita GUI")
        print("4. Exit")

        choice = input("\nPilih menu (1/2/3/4): ").strip()

        if choice == "1":
            print("\nMemulai proses training...")
            train_model(epochs=10)
        elif choice == "2":
            run_frontend_server()
        elif choice == "3":
            print("\nLaunching Adwaita GUI...")
            launch_gui()
        elif choice == "4":
            print("Keluar...")
            sys.exit(0)
        else:
            print("Pilihan tidak valid.")


if __name__ == "__main__":
    main()
