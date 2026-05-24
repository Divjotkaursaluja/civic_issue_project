import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image


# ---------- Model Path ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "final_model.keras")

CLASS_LABELS = [
    "potholes",
    "streetlight",
    "trash_bins",
    "unknown",
    "water_leakage",
]

_MODEL = None
_PREPROCESS_INPUT = None


def get_model():
    global _MODEL, _PREPROCESS_INPUT

    if _MODEL is None:
        import tensorflow as tf
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

        _PREPROCESS_INPUT = preprocess_input
        _MODEL = tf.keras.models.load_model(
            MODEL_PATH,
            compile=False,
            safe_mode=False,
        )
        print("AI MODEL LOADED")

    return _MODEL, _PREPROCESS_INPUT


def classify_image(file_input):
    print("AI INFERENCE RUNNING")

    import numpy as np

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
        model, preprocess_input = get_model()
        img = preprocess_input(img)

        print("STEP 5")

        preds = model.predict(img)

        print("PREDICTION DONE")
        print("RAW PREDS:", preds)

        preds = preds[0]

        index = np.argmax(preds)
        confidence = float(preds[index])
        label = CLASS_LABELS[index]

        print("FINAL LABEL:", label)
        print("CONFIDENCE:", confidence)

        return label, confidence

    except Exception:
        import traceback

        print("FULL ERROR:")
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

    label, confidence = classify_image(uploaded_file)

    return JsonResponse({
        "predicted_class": label,
        "confidence": confidence,
    })
