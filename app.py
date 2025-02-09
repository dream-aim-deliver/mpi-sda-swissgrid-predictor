import os
from typing import Literal
from flask import Flask, request, jsonify
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np


MODEL_BASEPATH = "/model_files"
SUPPORTED_MODELS = ["unified", "beznau"]
KP_HOST = os.getenv("KP_HOST")
KP_PORT = os.getenv("KP_PORT")
KP_SCHEME = os.getenv("KP_SCHEME")
KP_AUTH_TOKEN = os.getenv("KP_AUTH_TOKEN")


if any(v is None for v in [KP_HOST, KP_PORT, KP_SCHEME, KP_AUTH_TOKEN]):
    raise ValueError("Please set all environment variables: KP_HOST, KP_PORT, KP_SCHEME, KP_AUTH_TOKEN")


def probability_to_prediction(probability: int) -> Literal["ON", "OFF"]:
    return "ON" if probability > 0.5 else "OFF"

def probability_to_confidence(probability: int) -> float:
    return probability if probability > 0.5 else 1 - probability



app = Flask(__name__)
with tf.device("/CPU:0"):
    unified_model = load_model(os.path.join(MODEL_BASEPATH, "Unified_model.keras"))
    beznau_model = load_model(os.path.join(MODEL_BASEPATH, "Unified_Beznau_model.keras"))


@app.route('/')
def home():
    return "Fast API running"


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Log the incoming request
        print("Received request:", request.json)

        data = request.json  # Expect JSON payload 

        images = data['images']
        if not data or 'images' not in data:
            return jsonify({'error': 'Invalid input. JSON with key "images" is required.'}), 400

        if len(images) != 5:
            return jsonify({"error": f"Exactly 5 images required, Received {len(images)}."}),400

        original_model_name = data['model_name']
        model_name = original_model_name.strip().lower()
        if model_name not in SUPPORTED_MODELS:
            return jsonify({"error": f"Invalid model name '{original_model_name}'. Please choose from {SUPPORTED_MODELS}"}), 400

        preprocessed_images = []
        target_size = (256, 256)
       
        for image in data['images']:
            img = load_img(image, target_size=target_size)
            img_array = img_to_array(img) / 255.0  # Normalize to [0, 1]
            preprocessed_images.append(img_array)
        combined_images = np.concatenate(preprocessed_images, axis=-1)

        # Make predictions
        if model_name == 'unified':
            predictions = unified_model.predict(np.expand_dims(combined_images, axis=0))  # Add batch dimension

            probability = predictions.tolist()[0][0]

            prediction = probability_to_prediction(probability) 
            confidence = probability_to_confidence(probability)

            return jsonify({
                'data': [
                    {
                        'label': model_name,
                        'prediction': prediction,
                        'confidence': confidence
                    }
                ]
            })
                

        elif model_name == 'beznau':
            predictions = beznau_model.predict(np.expand_dims(combined_images, axis=0)) # Add batch dimension
            nested_prob_1, nested_prob_2 = (pred.tolist() for pred in predictions)

            probability_1 = nested_prob_1[0][0]
            prediction_1 = probability_to_prediction(probability_1) 
            confidence_1 = probability_to_confidence(probability_1) 

            probability_2 = nested_prob_2[0][0]
            prediction_2 = probability_to_prediction(probability_2)
            confidence_2 = probability_to_confidence(probability_2) 

            return jsonify({
                'data': [
                    {
                        'label': f"{model_name}_tower_1",
                        'prediction': prediction_1,
                        'confidence': confidence_1
                    },
                    {
                        'label': f"{model_name}_tower_2",
                        'prediction': prediction_2,
                        'confidence': confidence_2
                    }
                ]
            })

        else:
            return jsonify({"error": f"Invalid model name. Please choose from {SUPPORTED_MODELS}"}), 400

    except Exception as e:
        print("Error during prediction: ", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)




# #sentinel data
#     kernel_planckster, protocol, file_repository = setup(
#                 job_id=job_id,
#                 logger=logger,
#                 kp_auth_token=kp_auth_token,
#                 kp_host=kp_host,
#                 kp_port=kp_port,
#                 kp_scheme=kp_scheme,
#             )

#     scraped_data_repository = ScrapedDataRepository(
#                 protocol=protocol,
#                 kernel_planckster=kernel_planckster,
#                 file_repository=file_repository,
#             )

    # data = request.json  # Expect JSON payload
    # images = np.array(data['images'])  # Input images as a NumPy array
    # predictions = model.predict(images)
    # return jsonify({'predictions': predictions.tolist()})