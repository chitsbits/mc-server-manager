import sys
from bson.json_util import dumps

from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from flask_pymongo import PyMongo, ObjectId
from pymongo import ReturnDocument

from helpers import *

app = Flask(__name__)
# CORS(app)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://admin:password@server-templates-db-sv.default.svc.cluster.local:27017/mcTemplatesDb?authSource=admin"
mongo = PyMongo(app)

@app.route('/')
def index():
    return jsonify({"message": "Server Templates Service, connected to MongoDB!"})


"""
/template
"""
@app.route('/template', methods=['GET'])
def get_templates():
    templates = mongo.db.serverTemplates.find({})
    count = mongo.db.serverTemplates.count_documents({})

    print('test', file=sys.stderr)
    
    template_list = {
        "templates": format_document_response(list(templates)),
        "count": count
    }

    return jsonify(template_list), 200


@app.route('/template', methods=['POST'])
def create_template():
    server_template = request.json
    mongo.db.serverTemplates.insert_one(server_template)

    return jsonify({"message": "Server template created successfully"}), 201


"""
/template/<template_id>
"""
@app.route('/template/<template_id>', methods=['GET'])
def get_template(template_id):
    result = mongo.db.serverTemplates.find_one({"_id": ObjectId(template_id)})

    if result is None:
        return jsonify({"message": "Template not found"}), 404

    return jsonify(format_document_response(result)), 200


@app.route('/template/<template_id>', methods=['PUT'])
def update_template(template_id):
    update_data = request.json

    # Validate template_id
    try:
        template_id = ObjectId(template_id)
    except Exception:
        return jsonify({"error": "Invalid template ID"}), 400

    updated_template = mongo.db.serverTemplates.find_one_and_update(
        {"_id": ObjectId(template_id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    if updated_template is None:
        return jsonify({"message": "Template not found"}), 404

    return jsonify(format_document_response(updated_template)), 201
    

@app.route('/template/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    mongo.db.serverTemplates.delete_one({"_id": ObjectId(template_id)})

    return jsonify({"message": "Server template deleted successfully"}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0")