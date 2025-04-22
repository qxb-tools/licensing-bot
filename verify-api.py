from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from waitress import serve
from dotenv import load_dotenv  # Import dotenv loader
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    filename='server.log',  # Log to file "server.log"
    level=logging.INFO,  # Log info, warnings, and errors
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

# Connect to MongoDB Atlas (Read from loaded environment variables)
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    logging.error("MONGO_URI is not set in environment variables.")
    raise ValueError("MONGO_URI is not set in environment variables.")

client = MongoClient(MONGO_URI)
db = client['licenseDB']
licenses_collection = db['licenses']

# License validation API endpoint (GET request)
@app.route('/validate', methods=['GET'])
def validate_license():
    """
    API endpoint to validate a license key.
    Expects a query parameter: ?license_key=<license_key>
    """
    license_key = request.args.get('license_key')

    if not license_key:
        logging.warning("License key not provided in request.")
        return jsonify({"valid": False, "message": "License key is required Contact @dxbtrenches"}), 400

    logging.info(f"Validating license key: {license_key}")
    license_entry = licenses_collection.find_one({"license_key": license_key})

    if license_entry:
        if license_entry.get("used"):
            logging.info(f"License key '{license_key}' has already been used.")
            return jsonify({"valid": False, "message": "License Invalid used Contact @dxbtrenches"}), 400
        logging.info(f"License key '{license_key}' is valid.")
        return jsonify({"valid": True, "message": "VALID"}), 200
    else:
        logging.info(f"Invalid or expired license key: {license_key}")
        return jsonify({"valid": False, "message": "Invalid or expired license key Contact @dxbtrenches"}), 401


# Mark license as used API endpoint (POST request)
@app.route('/mark_used', methods=['POST'])
def mark_license_as_used():
    """
    API endpoint to mark a license key as used.
    Expects JSON input: {"license_key": "<license_key>"}
    """
    data = request.get_json()
    license_key = data.get('license_key')

    if not license_key:
        logging.warning("License key not provided in POST request.")
        return jsonify({"status": "error", "message": "License key is required"}), 400

    logging.info(f"Marking license key '{license_key}' as used.")
    result = licenses_collection.update_one(
        {"license_key": license_key},
        {"$set": {"used": True}}
    )

    if result.matched_count > 0:
        logging.info(f"License key '{license_key}' successfully marked as used.")
        return jsonify({"status": "success", "message": "License key marked as used"}), 200
    else:
        logging.error(f"License key '{license_key}' not found in the database.")
        return jsonify({"status": "error", "message": "License key not found"}), 404


if __name__ == '__main__':
    # Serve the app in production mode using Waitress WSGI server
    logging.info("Starting Flask app in production mode...")
    print("Starting Flask app in production mode...")
    serve(app, host='0.0.0.0', port=5050)
