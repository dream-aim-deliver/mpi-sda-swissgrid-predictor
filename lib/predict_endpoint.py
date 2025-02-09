from typing import List
from flask import request, jsonify
from lib.utils import probability_to_confidence, probability_to_prediction
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np



def predict_function(SUPPORTED_MODELS: List[str], unified_model, beznau_model):
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