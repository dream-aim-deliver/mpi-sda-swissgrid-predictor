import os
import traceback
from typing import List
from flask import request, jsonify
from lib.sdk.file_repository import FileRepository
from lib.sdk.kernel_plackster_gateway import KernelPlancksterGateway
from lib.sdk.models import KernelPlancksterSourceData, ProtocolEnum
from lib.sdk.utils import parse_relative_path
from lib.utils import probability_to_confidence, probability_to_prediction
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np


# WARNING: neither these nor the file names should contain "_" in their evalscript names
IMAGE_SEQUENCE = ("thermal", "natural", "optical-thickness", "moisture", "chlorophyll")


def predict_function(
    SUPPORTED_MODELS: List[str],
    unified_model,
    beznau_model,
    kernel_planckster_gateway: KernelPlancksterGateway,
    file_repository: FileRepository,
    ):

    # Log the incoming request
    print("Received request:", request.json)

    data = request.json  # Expect JSON payload 

    # Validate inputs
    required_keys = ['relative_paths', 'model_name']
    if not data or not all(key in data for key in required_keys):
        return jsonify({'error': f'Invalid input. JSON with keys {required_keys} is required.'}), 400 

    relative_paths = data['relative_paths']
    if not data:
        return jsonify({'error': 'Invalid input. JSON with key "images" is required.'}), 400

    if len(relative_paths) != 5:
        return jsonify({"error": f"Exactly 5 relative paths required, Received {len(relative_paths)}."}), 400

    original_model_name = data['model_name']
    model_name = original_model_name.strip().lower()
    if model_name not in SUPPORTED_MODELS:
        return jsonify({"error": f"Invalid model name '{original_model_name}'. Please choose from {SUPPORTED_MODELS}"}), 400

    # Download images from Kernel Planckster
    images = []
    base_dir = 'images'
    os.makedirs(base_dir, exist_ok=True)

    try:

        for i, relative_path in enumerate(relative_paths):
            try:
                parsed_rp = parse_relative_path(relative_path)
            except Exception as e:
                return jsonify({
                    "error": f"Failed to parse relative path for image {i+1}, '{relative_path}'.",
                    "details": str(e),
                    "error_type": e.__class__.__name__,
                    "traceback": traceback.format_exc(),
                }), 400

            if IMAGE_SEQUENCE[i] not in parsed_rp.evalscript_name:
                return jsonify({"error": f"Invalid image sequence for image {i+1}. Expected '{IMAGE_SEQUENCE[i]}' in evalscript name, got '{parsed_rp.evalscript_name}'."}), 400

            source_datum = KernelPlancksterSourceData(
                name=f"{parsed_rp.image_hash}_{parsed_rp.evalscript_name}",
                protocol = ProtocolEnum.S3,
                relative_path = parsed_rp.to_str()
            )

            signed_url = kernel_planckster_gateway.generate_signed_url_for_download(source_datum)

            file_name = f"{parsed_rp.timestamp}_{parsed_rp.evalscript_name}.{parsed_rp.file_extension}"
            local_file_name = file_repository.public_download(
                signed_url=signed_url,
                file_path=os.path.join(base_dir, file_name)
            )

            full_path = os.path.abspath(local_file_name)
            images.append(full_path)

        # Preprocess images
        preprocessed_images = []
        target_size = (256, 256)
        
        for image in images:
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


    except Exception as e:
        return jsonify({
            "error": f"Failed to make prediction for model '{model_name}'.",
            "details": str(e),
            "error_type": e.__class__.__name__,
            "traceback": traceback.format_exc(),
        }), 500


    finally:
        # Cleanup images
        for image in images:
            if os.path.exists(image):
                os.remove(image)