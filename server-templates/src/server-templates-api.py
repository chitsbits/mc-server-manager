from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_pymongo import PyMongo

app = Flask(__name__)
CORS(app)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://admin:password@server-templates-db-sv.default.svc.cluster.local:27017/mcTemplatesDb?authSource=admin"
mongo = PyMongo(app)

@app.route('/')
def index():
    template = mongo.db.serverTemplates.find_one({"templateName": "Survival Mode"})

    return jsonify(message=f"Server Templates Service, connected to MongoDB! {template}")


@app.route('/template', methods=['POST'])
def create_template():
    server_template = request.json
    mongo.db.serverTemplates.insert_one(server_template)

    return jsonify(message="Server template created successfully"), 201


@app.route('/template/<template_id>', methods=['PUT'])
def update_template(template_id):
    updates = request.json
    mongo.db.serverTemplates.update_one({"_id": template_id}, {"$set": updates})

    return jsonify(message="Server template updated successfully"), 200


@app.route('/template/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    mongo.db.serverTemplates.delete_one({"_id": template_id})

    return jsonify(message="Server template deleted successfully"), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0")