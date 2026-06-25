import cv2
import asyncio
import websockets
import json
import numpy as np
import threading
import os

# Configuration
WS_URL = "ws://127.0.0.1:8000/ws/predict"
ROI_SIZE = 250

class RealtimeClassifier:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        # Load Face Detector untuk diabaikan (Exclusion)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        self.latest_result = "Mencari Buah..."
        self.latest_confidence = 0
        self.latest_rotten = 0
        self.running = True
        self.current_roi_frame = None
        
        self.roi_x, self.roi_y = 320, 240 # Default center
        self.target_x, self.target_y = 320, 240
        self.smooth_factor = 0.15

    async def send_frames(self):
        async with websockets.connect(WS_URL) as websocket:
            while self.running:
                if self.current_roi_frame is not None and self.current_roi_frame.size > 0:
                    try:
                        _, buffer = cv2.imencode('.jpg', self.current_roi_frame)
                        await websocket.send(buffer.tobytes())
                        response = await websocket.recv()
                        result = json.loads(response)
                        self.latest_result = result.get("prediction", "Unknown")
                        self.latest_confidence = result.get("confidence", 0) * 100
                        self.latest_rotten = result.get("rotten_percentage", 0)
                    except: pass
                await asyncio.sleep(0.06)

    def start_ws_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try: loop.run_until_complete(self.send_frames())
        except: self.latest_result = "API Offline"

    def run(self):
        ws_thread = threading.Thread(target=self.start_ws_thread, daemon=True)
        ws_thread.start()

        print("Smart Face-Aware Tracker Aktif. Tekan 'q' untuk keluar.")

        while True:
            ret, frame = self.cap.read()
            if not ret: break
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            # --- COMPUTER VISION: FILTERING ---
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 1. Deteksi Wajah (Untuk diabaikan)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # 2. Buat Mask untuk area buah (Color-based + Saliency)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # Range warna buah (Merah, Kuning, Hijau, Oranye)
            lower_fruit = np.array([0, 50, 50])
            upper_fruit = np.array([100, 255, 255])
            mask = cv2.inRange(hsv, lower_fruit, upper_fruit)
            
            # 3. EXCLUSION: Hapus area wajah dari mask tracking
            for (fx, fy, fw, fh) in faces:
                # Perbesar area wajah sedikit agar lebih aman
                cv2.rectangle(mask, (fx-20, fy-20), (fx+fw+20, fy+fh+20), 0, -1)
                # Visualisasi deteksi wajah yang diabaikan
                cv2.rectangle(frame, (fx, fy), (fx+fw, fy+fh), (0, 0, 255), 1)
                cv2.putText(frame, "MANUSIA (DIABAIKAN)", (fx, fy-5), 1, 0.8, (0, 0, 255), 1)

            # 4. Cari Kontur Buah di sisa mask
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                c = max(contours, key=cv2.contourArea)
                if cv2.contourArea(c) > 3000:
                    M = cv2.moments(c)
                    if M["m00"] != 0:
                        self.target_x = int(M["m10"] / M["m00"])
                        self.target_y = int(M["m01"] / M["m00"])

            # Smoothing
            self.roi_x += int((self.target_x - self.roi_x) * self.smooth_factor)
            self.roi_y += int((self.target_y - self.roi_y) * self.smooth_factor)

            x1 = max(0, min(w - ROI_SIZE, self.roi_x - ROI_SIZE // 2))
            y1 = max(0, min(h - ROI_SIZE, self.roi_y - ROI_SIZE // 2))
            x2, y2 = x1 + ROI_SIZE, y1 + ROI_SIZE
            self.current_roi_frame = frame[y1:y2, x1:x2].copy()

            # --- UI ---
            color = (0, 255, 0) if self.latest_confidence > 70 else (0, 255, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
            # Garis bidik (Crosshair)
            cv2.line(frame, (self.roi_x-10, self.roi_y), (self.roi_x+10, self.roi_y), color, 2)
            cv2.line(frame, (self.roi_x, self.roi_y-10), (self.roi_x, self.roi_y+10), color, 2)
            
            # Status Overlay
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (380, 110), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
            
            cv2.putText(frame, f"DETEKSI: {self.latest_result}", (15, 35), 1, 1.8, (255, 255, 255), 2)
            cv2.putText(frame, f"CONFIDENCE: {self.latest_confidence:.1f}%", (15, 65), 1, 1.2, (0, 255, 0), 2)
            cv2.putText(frame, f"KEBUSUKAN: {self.latest_rotten:.1f}%", (15, 95), 1, 1.2, (0, 0, 255), 2)

            cv2.imshow('Fruit Face-Aware Tracker', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    classifier = RealtimeClassifier()
    classifier.run()
