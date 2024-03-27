from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_pymongo import PyMongo

app = Flask(__name__)
CORS(app)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/mcServerConfigs"
mongo = PyMongo(app)

@app.route('/')
def index():
    return jsonify(message="Server Configuration Service")


@app.route('/config', methods=['POST'])
def create_config():
    server_config = request.json
    mongo.db.serverConfigs.insert_one(server_config)

    return jsonify(message="Server config created successfully"), 201


@app.route('/config/<config_id>', methods=['PUT'])
def update_config(config_id):
    updates = request.json
    mongo.db.serverConfigs.update_one({"_id": config_id}, {"$set": updates})

    return jsonify(message="Server config updated successfully"), 200


@app.route('/config/<config_id>', methods=['DELETE'])
def delete_config(config_id):
    mongo.db.serverConfigs.delete_one({"_id": config_id})

    return jsonify(message="Server config deleted successfully"), 200


if __name__ == '__main__':
    app.run(debug=True)