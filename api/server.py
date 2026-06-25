from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from src.predict import FruitClassifier
import shutil
import os
import json

app = FastAPI(title="Fruit Classification API")
classifier = FruitClassifier()

@app.post("/predict")
async def predict_fruit(file: UploadFile = File(...)):
    # Simpan file sementara
    temp_path = f"outputs/temp_{file.filename}"
    os.makedirs("outputs", exist_ok=True)
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Reload model jika baru saja di-training
    if classifier.model is None:
        classifier.load()
        
    result = classifier.predict(temp_path)
    
    # Hapus temp file
    os.remove(temp_path)
    
    return result

@app.websocket("/ws/predict")
async def websocket_predict(websocket: WebSocket):
    await websocket.accept()
    if classifier.model is None:
        classifier.load()
        
    try:
        while True:
            # Terima data gambar (bytes)
            data = await websocket.receive_bytes()
            
            # Prediksi
            result = classifier.predict_bytes(data)
            
            # Kirim hasil
            await websocket.send_json(result)
    except WebSocketDisconnect:
        print("Client disconnected from WebSocket")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()

@app.get("/")
def read_root():
    return {"status": "Fruit Classifier API is running", "model_loaded": classifier.model is not None}
