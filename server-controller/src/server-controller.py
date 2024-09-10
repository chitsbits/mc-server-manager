import time
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from kubernetes import client, config

import sys
import subprocess
import logging

from uuid import uuid4
from mcstatus import JavaServer

config.load_incluster_config()

k8s_core_v1 = client.CoreV1Api()
k8s_apps_v1 = client.AppsV1Api()

app = Flask(__name__)
# CORS(app, origins=["http://localhost:3000"])

def helm_install_server(server_id, chart_name, values):
    try:
        print(values)
        command = [
            "helm", "install", server_id,
            "--set", f"minecraftServer.serviceType=NodePort",
            "--set", f"minecraftServer.query.enabled={values.get('minecraftServer', {}).get('query', {}).get('enabled', True)}",            "--set", f"minecraftServer.nodePort={values.get('minecraftServer', {}).get('nodePort', 30000)}",
            "--set", f"minecraftServer.eula={values.get('minecraftServer', {}).get('eula', 'TRUE')}",
            "--set", f"minecraftServer.gameMode={values.get('minecraftServer', {}).get('gameMode', 'survival')}",
            "--set", f"minecraftServer.version={values.get('minecraftServer', {}).get('version', 'LATEST')}",
            "--set", f"minecraftServer.type={values.get('minecraftServer', {}).get('type', 'VANILLA')}",
            "--set", f"minecraftServer.difficulty={values.get('minecraftServer', {}).get('difficulty', 'easy')}",
            "--set", f"minecraftServer.maxPlayers={values.get('minecraftServer', {}).get('maxPlayers', 20)}",
            "--set", f"minecraftServer.motd={values.get('minecraftServer', {}).get('motd', 'test motd!')}",
            "--set", f"persistence.dataDir.enabled={values.get('persistence', {}).get('dataDir', {}).get('enabled', False)}",
            chart_name
            # "--post-renderer", "/app/src/helm-post-renderer.py"
        ]
        print(command)

        # Add serverName as a quoted string
        # server_name = values.get('serverName', 'Minecraft Server')

        # # Ensure server_name is properly handled as a string with spaces
        # command.append(server_name)

        # Run the Helm command
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error during Helm install: {e.stderr}, {e.stdout}"


# Function to run Helm uninstall to delete the server
def helm_uninstall_server(server_id):
    try:
        # Helm uninstall command to delete the release
        command = [
            "helm", "uninstall", server_id
        ]

        # Execute the command
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout

    except subprocess.CalledProcessError as e:
        return f"Error during Helm uninstall: {e.stderr}"


# Function to run Helm upgrade to scale the server to 1 replica (start the server)
def helm_scale_up(server_id):
    try:
        # Helm upgrade command to update the replica count to 1
        command = [
            "helm", "upgrade", server_id, "itzg/minecraft",
            "--reuse-values",  # Reuse existing values
            "--set", "replicaCount=1"  # Set replicas to 1 (start the server)
        ]

        # Execute the command
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout

    except subprocess.CalledProcessError as e:
        return f"Error during Helm scale up: {e.stderr}"


# Function to run Helm upgrade to scale the server down to 0 replicas
def helm_scale_down(server_id):
    try:
        # Helm upgrade command to update the replica count to 0
        command = [
            "helm", "upgrade", server_id, "itzg/minecraft",
            "--reuse-values",  # Reuse existing values
            "--set", "replicaCount=0"
        ]

        # Execute the command
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout

    except subprocess.CalledProcessError as e:
        return f"Error during Helm scale down: {e.stderr}"


# Function to get the list of Helm deployments and their replica count
def get_helm_deployments():
    try:
        # Helm list command to get all releases
        command = ["helm", "list", "--all", "--output", "json"]
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        releases = result.stdout
        
        # Parse the releases (as JSON)
        releases_list = eval(releases)  # Or use json.loads(releases) if Helm outputs JSON format

        # Collect deployment statuses
        deployments = []

        for release in releases_list:
            # Fetch the release name and namespace
            release_name = release['name']
            namespace = release['namespace']

            # Get the deployment corresponding to the Helm release
            try:
                deployment = k8s_apps_v1.read_namespaced_deployment(name=f"{release_name}-minecraft", namespace=namespace)
                replica_count = deployment.spec.replicas
                status = "running" if replica_count > 0 else "stopped"
                
                deployments.append({
                    "release": release_name,
                    "replicaCount": replica_count,
                    "status": status
                })
            except client.exceptions.ApiException as e:
                deployments.append({
                    "release": release_name,
                    "status": "error fetching status",
                    "error": str(e)
                })

        return deployments

    except subprocess.CalledProcessError as e:
        return {"error": f"Error fetching Helm deployments: {e.stderr}"}


def get_server_k8s_data():
    # List all deployments in the namespace
    try:
        deployments = k8s_apps_v1.list_namespaced_deployment(namespace="default")
    except client.exceptions.ApiException as e:
        print(f"Error fetching deployments: {e}")
        return []

    # Filter deployments that start with "mc-"
    mc_deployments = [deploy for deploy in deployments.items if deploy.metadata.name.startswith("mc-")]

    server_statuses = []
    for deployment in mc_deployments:
        # Fetch deployment-specific details
        server_id = deployment.metadata.labels.get('release')
        name = deployment.metadata.name
        available_replicas = deployment.status.available_replicas if deployment.status.available_replicas else 0
        status = "Running" if available_replicas > 0 else "Stopped"

        # Try to get the Service associated with this deployment
        try:
            service = k8s_core_v1.read_namespaced_service(name=name, namespace="default")
            # Extract the port from the service spec
            port = service.spec.ports[0].node_port if service.spec.ports[0].node_port else service.spec.ports[0].port
        except client.exceptions.ApiException as e:
            print(f"Error fetching service for {name}: {e}")
            port = None  # Default to None if no service found

        server_statuses.append({
            "name": name,
            "server_id": server_id,
            "replicas": available_replicas,
            "status": status,
            "port": port,
        })

    return server_statuses


def combined_k8s_and_query_server_data():
    mc_k8s_info = get_server_k8s_data()
    print(mc_k8s_info)
    server_data = []

    for k8s_server_info in mc_k8s_info:
        if k8s_server_info.get('status') == "Running":
            # Connect using the service's name
            print("connecting using argument: ", f"{k8s_server_info.get('name')}.default.svc.cluster.local", 25565)

            server = JavaServer(f"{k8s_server_info.get('name')}.default.svc.cluster.local", 25565)
            status = server.status()

            server_data.append({
                'name': k8s_server_info['name'],
                'server_id': k8s_server_info['server_id'],
                'port': k8s_server_info['port'],
                'status': k8s_server_info['status'],
                **status.raw
            })
        else:
            server_data.append({
                'name': k8s_server_info['name'],
                'server_id': k8s_server_info['server_id'],
                'port': k8s_server_info['port'],
                'status': k8s_server_info['status'],
            })

    return server_data

@app.route("/")
def hello():
    logging.debug("root!")
    return "Hello from Python!"


@app.route("/list")
def get_servers_list():
    # deployments = get_helm_deployments()
    statuses = get_server_k8s_data()
    return jsonify(statuses)


# @app.route("/status")
# def get_server_status():
#     statuses = combined_k8s_and_query_server_data()
#     return jsonify(statuses)


@app.route("/status/all")
def status_stream():
    def event_stream():
        with app.app_context():
            while True:
                statuses = combined_k8s_and_query_server_data()
                yield f"data: {jsonify(statuses).get_data(as_text=True)}\n\n"
                time.sleep(5)  # Simulating data streaming every 5 seconds

    return Response(event_stream(), mimetype="text/event-stream")


@app.delete("/<server_id>")
def delete_server(server_id):
    # Call the function to uninstall the server
    output = helm_uninstall_server(server_id)
    if "Error" in output:
        return jsonify({"error": output}), 500

    return jsonify({"message": f"Successfully deleted server {server_id}", "output": output}), 200


@app.post("/create-server")
def create_server():
    # Extract server details from the request body
    server_values = request.get_json()

    # Example values from request body
    server_id = "mc-" + str(uuid4())
    print(server_values)

    # Call the Helm install function
    chart_name = "itzg/minecraft"  # Path to the Helm chart
    install_output = helm_install_server(server_id, chart_name, server_values)

    return jsonify({"message": "Server created", "output": install_output})


@app.post("/<server_id>/stop")
def stop_server(server_id):
    # Call the function to scale down the server
    output = helm_scale_down(server_id)
    if "Error" in output:
        return jsonify({"error": output}), 500

    return jsonify({"message": f"Successfully stopped server {server_id}", "output": output}), 200


@app.post("/<server_id>/start")
def start_server(server_id):
    # Call the function to scale up the server
    output = helm_scale_up(server_id)
    if "Error" in output:
        return jsonify({"error": output}), 500

    return jsonify({"message": f"Successfully started server {server_id}", "output": output}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0")
