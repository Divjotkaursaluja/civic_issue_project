import tensorflow as tf

model = tf.keras.models.load_model(
    "ai_model/model.h5",
    compile=False
)

print("✅ Model loaded!")

model.save("ai_model/model.keras")

print("✅ Converted successfully!")