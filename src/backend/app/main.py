from flask import Flask
from kubernetes import client, config
	
config.load_incluster_config()
k8s_core_v1 = client.CoreV1Api()
k8s_apps_v1 = client.AppsV1Api()

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Python!"

@app.route("/list")
def get_pods_list():
    pods_list = k8s_core_v1.list_namespaced_pod(namespace='default')
    pods = [item.metadata.name for item in pods_list.items]

    return pods

@app.route("/fetch")
def fetch():
    pass

@app.route("/stop-server/<id>")
def stop_server():
    pass

@app.route("/create-server")
def create_server():
    e_eula = client.V1EnvVar(name="EULA", value="TRUE")

    # Apply the Deployment to the cluster
    try:
        # Create service to access the MC server port
        k8s_core_v1.create_namespaced_service(
            namespace="default",
            body=client.V1Service(
                api_version="v1",
                kind="Service",
                metadata=client.V1ObjectMeta(name="mc-server-service"),
                spec=client.V1ServiceSpec(
                    type="LoadBalancer",
                    selector={"app": "minecraft-server"},  # Select the pods to expose
                    ports=[client.V1ServicePort(protocol="TCP", port=25565, target_port=25565)]  # Define the ports
                )
            )
        )

        k8s_apps_v1.create_namespaced_deployment(
            namespace="default",  # Replace with the desired namespace
            body=client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=client.V1ObjectMeta(name="mc-server-1"),
                spec=client.V1DeploymentSpec(
                    replicas=1,
                    selector=client.V1LabelSelector(
                        match_labels={"app": "minecraft-server"}  # Specify the same labels as in pod_template_metadata
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={"app": "minecraft-server"}
                        ),
                        spec=client.V1PodSpec(
                            containers=[client.V1Container(
                                name="minecraft-server-container",
                                image="itzg/minecraft-server",
                                ports=[client.V1ContainerPort(container_port=25565)],
                                env=[e_eula]
                            )]
                        )
                    )
                )
            )
        )
        print("Deployment created successfully!")
        return "Success"
    except Exception as e:
        print(f"Error creating Deployment: {e}")
        return str(e)


if __name__ == "__main__":
    app.run(host='0.0.0.0')