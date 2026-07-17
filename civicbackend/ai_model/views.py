import json
import os
import tempfile
import zipfile

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image


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
_COMPATIBLE_MODEL_PATH = None


def _strip_empty_quantization_config(value):
    if isinstance(value, dict):
        return {
            key: _strip_empty_quantization_config(item)
            for key, item in value.items()
            if not (key == "quantization_config" and item is None)
        }
    if isinstance(value, list):
        return [_strip_empty_quantization_config(item) for item in value]
    return value


def get_compatible_model_path():
    global _COMPATIBLE_MODEL_PATH

    if _COMPATIBLE_MODEL_PATH is not None:
        return _COMPATIBLE_MODEL_PATH

    with zipfile.ZipFile(MODEL_PATH, "r") as source:
        config = json.loads(source.read("config.json"))
        clean_config = _strip_empty_quantization_config(config)

        if clean_config == config:
            _COMPATIBLE_MODEL_PATH = MODEL_PATH
            return _COMPATIBLE_MODEL_PATH

        fd, temporary_path = tempfile.mkstemp(suffix=".keras")
        os.close(fd)
        with zipfile.ZipFile(temporary_path, "w") as compatible:
            for entry in source.infolist():
                content = source.read(entry.filename)
                if entry.filename == "config.json":
                    content = json.dumps(clean_config).encode("utf-8")
                compatible.writestr(entry, content)

    _COMPATIBLE_MODEL_PATH = temporary_path
    print("AI MODEL COMPATIBILITY METADATA NORMALIZED")
    return _COMPATIBLE_MODEL_PATH


def get_model():
    global _MODEL, _PREPROCESS_INPUT

    if _MODEL is None:
        import tensorflow as tf
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

        _PREPROCESS_INPUT = preprocess_input
        _MODEL = tf.keras.models.load_model(
            get_compatible_model_path(),
            compile=False,
            safe_mode=False,
        )
        print("AI MODEL LOADED")

    return _MODEL, _PREPROCESS_INPUT


def classify_image(file_input):
    print("AI INFERENCE RUNNING")

    import numpy as np

    try:
        if not isinstance(file_input, str):
            file_input.seek(0)

        img = Image.open(file_input)
        img = img.convert("RGB")
        img = img.resize((224, 224))
        img = np.array(img)
        img = np.expand_dims(img, axis=0)

        model, preprocess_input = get_model()
        img = preprocess_input(img)
        preds = model.predict(img)
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
