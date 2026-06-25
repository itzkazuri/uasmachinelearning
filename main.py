import sys
import os
import subprocess
import shutil
from src.train import train_model
from gui.app import launch_gui
import uvicorn

def main():
    print("=== FRUIT CLASSIFICATION SYSTEM ===")
    print("1. Training Model (10 Epochs)")
    print("2. Start API & Frontend Server (FastAPI + Vite)")
    print("3. Launch Adwaita GUI")
    print("4. Exit")
    
    choice = input("\nPilih menu (1/2/3/4): ")
    
    if choice == '1':
        print("\nMemulai proses training...")
        train_model(epochs=10)
    elif choice == '2':
        if not os.path.exists('models/fruit_model.keras'):
            print("\nPERINGATAN: Model tidak ditemukan. Silakan pilih menu 1 dulu.")
            return
            
        # Tentukan package manager (bun atau npm)
        has_bun = shutil.which("bun") is not None
        pkg_manager = "bun" if has_bun else "npm"
        
        # Install node_modules jika belum ada
        if not os.path.exists("frontend/node_modules"):
            print(f"\nnode_modules tidak ditemukan di folder frontend. Menginstal dependensi menggunakan {pkg_manager}...")
            install_cmd = [pkg_manager, "install"]
            try:
                subprocess.run(install_cmd, cwd="frontend", check=True)
            except Exception as e:
                print(f"Gagal menginstal dependensi frontend: {e}")
                print("Silakan jalankan secara manual di folder 'frontend': npm install atau bun install")
                return

        # Mulai Vite Frontend
        vite_cmd = [pkg_manager, "run", "dev"]
        print(f"\nMemulai Vite Frontend di folder frontend ({' '.join(vite_cmd)})...")
        frontend_process = None
        try:
            frontend_process = subprocess.Popen(
                vite_cmd,
                cwd="frontend"
            )
            
            # Mulai FastAPI
            print("\nMemulai server FastAPI di http://127.0.0.1:8000")
            uvicorn.run("api.server:app", host="127.0.0.1", port=8000, reload=True)
        except KeyboardInterrupt:
            print("\nMenerima sinyal keluar...")
        except Exception as e:
            print(f"\nTerjadi kesalahan: {e}")
        finally:
            if frontend_process:
                print("\nMenghentikan Vite Frontend...")
                frontend_process.terminate()
                try:
                    frontend_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    frontend_process.kill()
                print("Vite Frontend berhasil dihentikan.")
                
    elif choice == '3':
        print("\nLaunching Adwaita GUI...")
        launch_gui()
    elif choice == '4':
        print("Keluar...")
        sys.exit(0)
    else:
        print("Pilihan tidak valid.")

if __name__ == "__main__":
    main()

