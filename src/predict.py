
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import os

class FruitClassifier:
    def __init__(self, model_path='models/fruit_model.keras', class_path='models/class_names.txt'):
        self.model_path = model_path
        self.class_path = class_path
        self.model = None
        self.class_names = []
        self.load()

    def load(self):
        if os.path.exists(self.model_path):
            self.model = tf.keras.models.load_model(self.model_path)
        if os.path.exists(self.class_path):
            with open(self.class_path, 'r') as f:
                self.class_names = [line.strip() for line in f.readlines() if line.strip()]

    def preprocess_image(self, img):
        img = img.resize((224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0
        return img_array

    def predict(self, img_path):
        if not self.model:
            return {"error": "Model belum dilatih atau tidak ditemukan."}

        img = image.load_img(img_path)
        img_array = self.preprocess_image(img)
        return self._perform_prediction(img_array)

    def predict_bytes(self, img_bytes):
        if not self.model:
            return {"error": "Model belum dilatih atau tidak ditemukan."}

        from io import BytesIO
        from PIL import Image
        img = Image.open(BytesIO(img_bytes))
        img_array = self.preprocess_image(img)
        return self._perform_prediction(img_array)

    def _perform_prediction(self, img_array):
        predictions = self.model.predict(img_array)[0]
        top_index = np.argmax(predictions)
        
        # Persen Busuk
        rotten_indices = [i for i, name in enumerate(self.class_names) if 'rotten' in name.lower()]
        total_rotten_prob = sum([predictions[i] for i in rotten_indices])

        results = {
            "prediction": self.class_names[top_index],
            "confidence": float(predictions[top_index]),
            "rotten_percentage": float(total_rotten_prob * 100),
            "other_similarities": {
                self.class_names[i]: float(predictions[i] * 100) 
                for i in np.argsort(predictions)[::-1]
            }
        }
        return results
