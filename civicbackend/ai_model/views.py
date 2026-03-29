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
def classify_image(file_input):
    print("🔥🔥 NEW AI CODE RUNNING 🔥🔥")
    try:
        from PIL import Image
        import numpy as np
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

        # 🔥 HANDLE BOTH CASES (file OR path)
        print("🔥 classify_image called")
        if not isinstance(file_input, str):
            file_input.seek(0)

        img = Image.open(file_input)
        img = img.convert("RGB")   # ⚠️ IMPORTANT
        img = img.resize((224, 224))

        img = np.array(img)
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)

        model = tf.keras.models.load_model(MODEL_PATH, compile=False)

        preds = model.predict(img)
        print("DEBUG preds:", preds)   # 🔥 ADD THIS

        preds = preds[0]

        index = np.argmax(preds)
        confidence = float(preds[index])
        label = CLASS_LABELS[index]

        return label, confidence

    except Exception as e:
        print("AI error:", e)
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