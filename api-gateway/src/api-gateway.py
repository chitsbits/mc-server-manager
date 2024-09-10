import sys
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])


@app.get("/")
def hello():
    return "API Gateway Service"

# ----- Authentication/Authorization ------
# TODO


# ----- Server Controller -----

@app.get("/servers")
def get_server_list():
    try:
        response = requests.get('http://server-controller-sv:31003/status')
        return response.json()
    except Exception as e:
        return jsonify({"message": f"Error fetching server list"}), 500


@app.get("/servers/status/all")
def servers_status_stream():
    # Forward the SSE request to the backend
    backend_url = 'http://server-controller-sv:31003/status/all'  # Adjust to your backend URL

    def stream():
        with requests.get(backend_url, stream=True) as backend_response:
            for line in backend_response.iter_lines():
                if line:
                    yield f"data: {line.decode('utf-8')}\n\n"

    return Response(stream(), mimetype='text/event-stream')


@app.post("/servers/create")
def create_server():
    try:
        body = request.get_json()
        response = requests.post('http://server-controller-sv:31003/create-server', json=body)
        return response.json()
    except Exception as e:
        return jsonify({"message": f"Error creating server"}), 500


@app.post("/servers/<server_id>/start")
def start_server(server_id):
    try:
        response = requests.post(f"http://server-controller-sv:31003/{server_id}/start")
        return response.json()
    except Exception as e:
        return jsonify({"message": f"Error starting server"}), 500


@app.post("/servers/<server_id>/stop")
def stop_server(server_id):
    try:
        response = requests.post(f"http://server-controller-sv:31003/{server_id}/stop")
        return response.json()
    except Exception as e:
        return jsonify({"message": f"Error stopping server"}), 500


@app.delete("/servers/<server_id>")
def delete_server(server_id):
    try:
        response = requests.delete(f"http://server-controller-sv:31003/{server_id}")
        return response.json()
    except Exception as e:
        return jsonify({"message": f"Error deleting server"}), 500

# ----- Server Templates -----

@app.get("/server-templates")
def get_server_templates_list():
    try:
        response = requests.get('http://server-templates-api-sv:31002/template')
        print(response, file=sys.stderr)
        return response.json()
    except Exception as e:
        return jsonify({"message": f"Error fetching server list"}), 500


@app.get('/server-templates/<template_id>')
def get_server_template(template_id):
    pass


@app.post("/server-templates")
def create_server_template():
    pass


@app.put('/server-templates/<template_id>')
def update_server_template(template_id):
    pass


@app.delete("/server-templates/<template_id>")
def delete_server_template(template_id):
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0")
