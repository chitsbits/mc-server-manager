from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])


@app.get("/")
def hello():
    return "API Gateway Service"

# Authentication/Authorization
# TODO


# ----- Server Controller -----

@app.get("/servers")
def get_server_list():
    pass


@app.post("/servers/<server_id>/start")
def start_server(server_id):
    pass


@app.post("/servers/<server_id>/stop")
def stop_server(server_id):
    pass


# ----- Server Configurations -----

@app.get("/server-configs")
def get_server_configs_list():
    pass


@app.get('/server-configs/<config_id>')
def get_server_config(config_id):
    pass


@app.post("/server-configs")
def create_server_config():
    pass

@app.put('/server-configs/<config_id>')
def update_server_config(config_id):
    pass


@app.delete("/server-configs/<config_id>")
def delete_server_config(config_id):
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0")
