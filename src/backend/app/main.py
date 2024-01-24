from flask import Flask, jsonify, request
from kubernetes import client, config

import sys
import subprocess

from uuid import uuid4

config.load_incluster_config()

k8s_core_v1 = client.CoreV1Api()
k8s_apps_v1 = client.AppsV1Api()

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello from Python!"


@app.route("/list")
def get_pods_list():
    pods_list = k8s_core_v1.list_namespaced_pod(namespace="default")
    deployments_list = k8s_apps_v1.list_namespaced_deployment(namespace="default")
    persistent_volumes_list = k8s_core_v1.list_persistent_volume()
    persistent_volume_claims_list = k8s_core_v1.list_namespaced_persistent_volume_claim(
        namespace="default"
    )
    statefulsets = k8s_apps_v1.list_namespaced_stateful_set(namespace="default")

    pods = [
        {"name": item.metadata.name, "labels": item.metadata.labels}
        for item in pods_list.items
    ]
    deployments = [
        {
            "name": item.metadata.name,
            "labels": item.metadata.labels,
            "avail_replicas": item.status.available_replicas,
        }
        for item in deployments_list.items
    ]
    claims = [
        {
            "name": item.metadata.name,
            "labels": item.metadata.labels,
            "status": item.status.phase,
        }
        for item in persistent_volume_claims_list.items
    ]
    volumes = [
        {
            "name": item.metadata.name,
            "capacity": item.spec.capacity,
            "status": item.status.phase,
            "class": item.spec.storage_class_name,
        }
        for item in persistent_volumes_list.items
    ]
    statefulsets = [
        {
            "name": item.metadata.name,
            "labels": item.metadata.labels,
            "avail_replicas": item.status.available_replicas,
        }
        for item in statefulsets.items
    ]

    return {
        "pods": pods,
        "deployments": deployments,
        "statefulsets": statefulsets,
        "volumes": volumes,
        "claims": claims,
    }


@app.route("/fetch")
def fetch():
    pass


@app.route("/delete-server/<server_id>")
def delete_server(server_id):
    try:
        # Delete Statefulset of server
        k8s_apps_v1.delete_namespaced_stateful_set(
            name=f"mc-server-{server_id}",
            namespace="default",
            body=client.V1DeleteOptions(propagation_policy="Foreground"),
        )

        # Delete the service for the pod
        k8s_core_v1.delete_namespaced_service(
            name=f"mc-svc-{server_id}", namespace="default"
        )

        # Delete the headless service for the StatefulSet
        k8s_core_v1.delete_namespaced_service(
            name=f"mc-headless-svc-{server_id}", namespace="default"
        )

        # Delete PVC(s)
        pvc_list = k8s_core_v1.list_namespaced_persistent_volume_claim(
            namespace="default", label_selector=f"server-id={server_id}"
        )
        for pvc in pvc_list.items:
            try:
                k8s_core_v1.delete_namespaced_persistent_volume_claim(
                    name=pvc.metadata.name, namespace="default"
                )
                print(pvc.metadata.name, " deleted")
            except client.exceptions.ApiException as e:
                print(f"Error deleting PVC: {e}", file=sys.stderr)

        # Optionally, delete the manually created Persistent Volume if it's no longer needed
        k8s_core_v1.delete_persistent_volume(name=f"pv-{server_id}")

        # Delete hostpath files (if applicable)
        clean_hostpath_directory(server_id)

        return jsonify({"message": f"Deleted server with identifier {server_id}"}), 200
    except Exception as e:
        return jsonify({"error": f"Error deleting server {server_id}: {e}"}), 500


@app.post("/create-server")
def create_server():
    request_data = request.get_json()
    print(request_data, file=sys.stderr)

    # Apply the Deployment to the cluster
    try:
        server_id = str(uuid4())

        # Create service to access the MC server port
        k8s_core_v1.create_namespaced_service(
            namespace="default",
            body=client.V1Service(
                api_version="v1",
                kind="Service",
                metadata=client.V1ObjectMeta(name=f"mc-svc-{server_id}"),
                spec=client.V1ServiceSpec(
                    type="LoadBalancer",
                    selector={"app": "minecraft-server"},  # Select the pods to expose
                    ports=[
                        client.V1ServicePort(
                            protocol="TCP", port=25565, target_port=25565
                        )
                    ],  # Define the ports
                ),
            ),
        )

        # Create a persistent volume (PV) on the host (Docker Desktop VM ?)
        k8s_core_v1.create_persistent_volume(
            client.V1PersistentVolume(
                api_version="v1",
                kind="PersistentVolume",
                metadata=client.V1ObjectMeta(
                    name=f"pv-{server_id}",
                    labels={"type": "minecraft-volume", "server-id": server_id},
                ),
                spec=client.V1PersistentVolumeSpec(
                    capacity={"storage": "30Gi"},  # Adjust storage capacity as needed
                    volume_mode="Filesystem",  # Set to "Block" for raw block devices
                    access_modes=["ReadWriteOnce"],  # Adjust access mode as needed
                    persistent_volume_reclaim_policy="Delete",  # Adjust reclaim policy as needed
                    host_path=client.V1HostPathVolumeSource(
                        path=f"/var/lib/docker/volumes/mc/{server_id}/"
                    ),  # Specify the host path
                ),
            )
        )

        # Configure itzg/minecraft-server container
        env_list = []
        env_list.append(
            client.V1EnvVar(name="EULA", value="TRUE")
        )  # Mandatory EULA env var
        for k, v in request_data.items():
            env_list.append(client.V1EnvVar(name=k, value=v))

        itzg_container = client.V1Container(
            name="minecraft-server-container",
            image="itzg/minecraft-server",
            ports=[client.V1ContainerPort(container_port=25565)],
            env=env_list,
            volume_mounts=[
                client.V1VolumeMount(name=f"volume-{server_id}", mount_path="/data")
            ],
        )

        # Create headless service for StatefulSet
        k8s_core_v1.create_namespaced_service(
            namespace="default",
            body=client.V1Service(
                api_version="v1",
                kind="Service",
                metadata=client.V1ObjectMeta(name=f"mc-headless-svc-{server_id}"),
                spec=client.V1ServiceSpec(
                    cluster_ip="None",  # This makes the service headless
                    selector={
                        "app": "minecraft-server",  # This should match the label of your StatefulSet pods
                    },
                    ports=[client.V1ServicePort(protocol="TCP", port=25565)],
                ),
            ),
        )

        # Create PVC for the server
        pvc = client.V1PersistentVolumeClaim(
            api_version="v1",
            kind="PersistentVolumeClaim",
            metadata=client.V1ObjectMeta(
                name=f"pvc-{server_id}", labels={"server-id": server_id}
            ),
            spec=client.V1PersistentVolumeClaimSpec(
                access_modes=["ReadWriteOnce"],
                resources=client.V1ResourceRequirements(requests={"storage": "30Gi"}),
                selector=client.V1LabelSelector(
                    match_labels={"type": "minecraft-volume", "server-id": server_id}
                ),
                storage_class_name="",  # Set to an empty string to prevent dynamic provisioning
            ),
        )
        k8s_core_v1.create_namespaced_persistent_volume_claim(
            namespace="default", body=pvc
        )

        # Create the StatefulSet
        k8s_apps_v1.create_namespaced_stateful_set(
            namespace="default",  # Replace with the desired namespace
            body=client.V1StatefulSet(
                api_version="apps/v1",
                kind="StatefulSet",
                metadata=client.V1ObjectMeta(
                    name=f"mc-server-{server_id}", labels={"server-id": server_id}
                ),
                spec=client.V1StatefulSetSpec(
                    service_name=f"mc-headless-svc-{server_id}",  # Name of the service that governs this StatefulSet
                    replicas=1,
                    selector=client.V1LabelSelector(
                        match_labels={"app": "minecraft-server"}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={"app": "minecraft-server", "server-id": server_id}
                        ),
                        spec=client.V1PodSpec(
                            containers=[itzg_container],
                            volumes=[
                                client.V1Volume(
                                    name=f"volume-{server_id}",
                                    persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                        claim_name=f"pvc-{server_id}"
                                    ),
                                )
                            ],
                        ),
                    ),
                ),
            ),
        )

        print("StatefulSet created successfully!", file=sys.stderr)
        return (
            jsonify(
                {
                    "message": f"Successfully created server with id: {server_id}",
                    "server_id": server_id,
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"message": f"Error creating Deployment: {e}"}), 500


@app.get("/stop-server/<server_id>")
def stop_server(server_id):
    try:
        # Get the current Statefulset object
        stateful_set = k8s_apps_v1.read_namespaced_stateful_set(
            name=f"mc-server-{server_id}", namespace="default"
        )
        # Update the desired replica count to 0
        stateful_set.spec.replicas = 0
        # Apply the updated Statefulset object to the cluster
        k8s_apps_v1.replace_namespaced_stateful_set(
            name=f"mc-server-{server_id}", namespace="default", body=stateful_set
        )

        return (
            jsonify(
                {
                    "message": f"Successfully stopped server with id: {server_id}",
                    "server_id": server_id,
                }
            ),
            200,
        )
    except client.rest.ApiException as e:
        if e.status == 404:
            return (
                jsonify(
                    {
                        "message": f"Statefulset 'mc-server-{server_id}' not found in namespace 'default'."
                    }
                ),
                404,
            )
        else:
            return (
                jsonify(
                    {
                        "message": f"Error scaling down Statefulset 'mc-server-{server_id}' in namespace 'default': {e}"
                    }
                ),
                500,
            )


@app.get("/start-server/<server_id>")
def start_server(server_id):
    try:
        # Get the current StatefulSet object
        stateful_set = k8s_apps_v1.read_namespaced_stateful_set(
            name=f"mc-server-{server_id}", namespace="default"
        )
        # Update the desired replica count to 1
        stateful_set.spec.replicas = 1
        # Apply the updated StatefulSet object to the cluster
        k8s_apps_v1.replace_namespaced_stateful_set(
            name=f"mc-server-{server_id}", namespace="default", body=stateful_set
        )

        return (
            jsonify(
                {
                    "message": f"Successfully started server with id: {server_id}",
                    "server_id": server_id,
                }
            ),
            200,
        )
    except client.rest.ApiException as e:
        if e.status == 404:
            return (
                jsonify(
                    {
                        "message": f"Deployment 'mc-server-{server_id}' not found in namespace 'default'."
                    }
                ),
                404,
            )
        else:
            return (
                jsonify(
                    {
                        "message": f"Error scaling up Deployment 'mc-server-{server_id}' in namespace 'default': {e}"
                    }
                ),
                500,
            )


# Called after deleting a PV to also remove the hostpath dir.
def clean_hostpath_directory(server_id):
    subprocess.run(["rm", "-rf", f"/var/lib/docker/volumes/mc/{server_id}"])


if __name__ == "__main__":
    app.run(host="0.0.0.0")
