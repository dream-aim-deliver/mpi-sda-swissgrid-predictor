import logging
import os
import sys
from flask import Flask, jsonify
from lib.predict_endpoint import predict_function
from lib.setup import setup
from lib.local_predict_endpoint import local_predict_function
import tensorflow as tf
from tensorflow.keras.models import load_model


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

MODEL_BASEPATH = "/model_files"
SUPPORTED_MODELS = ["unified", "beznau"]

try: 
    KP_HOST = os.getenv("KP_HOST")
    KP_PORT = os.getenv("KP_PORT")
    KP_SCHEME = os.getenv("KP_SCHEME")
    KP_AUTH_TOKEN = os.getenv("KP_AUTH_TOKEN")

    if any(v is None for v in [KP_HOST, KP_PORT, KP_SCHEME, KP_AUTH_TOKEN]):
        raise ValueError("Please set all environment variables: KP_HOST, KP_PORT, KP_SCHEME, KP_AUTH_TOKEN")


    kernel_planckster_gateway, protocol_enum, file_repository = setup(
        logger=logger,
        kp_auth_token=KP_AUTH_TOKEN,
        kp_host=KP_HOST,
        kp_port=KP_PORT,
        kp_scheme=KP_SCHEME,
    )
except Exception as e:
    logger.error(f"Error during setup: {str(e)}")
    sys.exit(1)


app = Flask(__name__)
with tf.device("/CPU:0"):
    unified_model = load_model(os.path.join(MODEL_BASEPATH, "Unified_model.keras"))
    beznau_model = load_model(os.path.join(MODEL_BASEPATH, "Unified_Beznau_model.keras"))


@app.route('/')
def home():
    return "Fast API running"


@app.route('/local-predict', methods=['POST'])
def local_predict():
    try:
        return local_predict_function(SUPPORTED_MODELS, unified_model, beznau_model)

    except Exception as e:
        print("Error during prediction: ", str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/predict', methods=['POST'])
def predict():
    try:
        return predict_function(SUPPORTED_MODELS, unified_model, beznau_model)

    except Exception as e:
        print("Error during prediction: ", str(e))
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

