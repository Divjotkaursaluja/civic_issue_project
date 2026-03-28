from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import numpy as np
import tensorflow as tf
import os
import io
from PIL import Image

# ---------- Model Path ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.h5")

CLASS_LABELS = [
    "potholes",
    "streetlight",
    "trash_bins",
    "unknown",
    "water_leakage"
]

# ---------- AI Function ----------
def classify_image(uploaded_file):
    try:
        uploaded_file.seek(0)  # 🔥 RESET FILE POINTER

        img = Image.open(uploaded_file).convert("RGB")  # ✅ FIX
        img = img.resize((224, 224))

        img = np.array(img)
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)

        model = tf.keras.models.load_model(MODEL_PATH, compile=False)

        preds = model.predict(img)
        print("DEBUG preds:", preds)

        preds = preds[0]

        index = np.argmax(preds)
        confidence = float(preds[index])
        label = CLASS_LABELS[index]

        return label, confidence

    except Exception as e:
        import traceback
        traceback.print_exc()
        return "unknown", 0.0


# ---------- API ----------
@csrf_exempt
def predict_issue(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    # 🔥 USE AI FUNCTION HERE
    label, confidence = classify_image(uploaded_file)

    return JsonResponse({
        "predicted_class": label,
        "confidence": confidence
    })