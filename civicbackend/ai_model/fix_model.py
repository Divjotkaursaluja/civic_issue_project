import tensorflow as tf
import os

if __name__ == "__main__":

    MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.h5")
    FIXED_MODEL_PATH = os.path.join(os.path.dirname(__file__), "model_fixed.h5")

    print(f"🔍 Loading model from: {MODEL_PATH}")

    try:
        # model = tf.keras.models.load_model(MODEL_PATH)
        print("✅ Model loaded successfully!")

        if isinstance(model.input, list) and len(model.input) > 1:
            print(f"⚙️ Model has {len(model.input)} inputs — fixing...")

            new_input = model.input[0]
            new_output = model.output

            fixed_model = tf.keras.Model(inputs=new_input, outputs=new_output)
            fixed_model.save(FIXED_MODEL_PATH)
            print(f"✅ Fixed model saved at: {FIXED_MODEL_PATH}")
        else:
            print("✅ Model already fine")
            model.save(FIXED_MODEL_PATH)

    except Exception as e:
        print(f"❌ Error: {e}")