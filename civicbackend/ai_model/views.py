from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import tensorflow as tf
import numpy as np
import os
import io

from PIL import Image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input


# ---------- Model Path ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "final_model.keras")

CLASS_LABELS = [
    "potholes",
    "streetlight",
    "trash_bins",
    "unknown",
    "water_leakage"
]

def classify_image(file_input):
    print("🔥🔥 NEW AI CODE RUNNING 🔥🔥")

    from PIL import Image
    import numpy as np
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

    try:
        print("STEP 1")

        if not isinstance(file_input, str):
            file_input.seek(0)

        print("STEP 2")

        img = Image.open(file_input)

        print("STEP 3")

        img = img.convert("RGB")
        img = img.resize((224, 224))

        print("STEP 4")

        img = np.array(img)
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)

        print("STEP 5")

        model = tf.keras.models.load_model(
            MODEL_PATH,
            compile=False,
            safe_mode=False
        )

        print("✅ MODEL LOADED")

        preds = model.predict(img)

        print("✅ PREDICTION DONE")
        print("RAW PREDS:", preds)

        preds = preds[0]

        index = np.argmax(preds)
        confidence = float(preds[index])
        label = CLASS_LABELS[index]

        print("✅ FINAL LABEL:", label)

        return label, confidence

    except Exception as e:
        import traceback
        print("❌ FULL ERROR:")
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