# convert_model.py

import tensorflow as tf

model = tf.keras.models.load_model(
    "ai_model/model.h5",
    compile=False,
    safe_mode=False
)

model.save("ai_model/final_model.keras")