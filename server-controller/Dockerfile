FROM python:3.11-slim

# Install curl, tar, and other necessary utilities
RUN apt-get update && apt-get install -y curl ca-certificates && \
    apt-get clean

# Install Helm
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Add the itzg Minecraft server Helm chart repository
RUN helm repo add itzg https://itzg.github.io/minecraft-server-charts && helm repo update

RUN mkdir /app
WORKDIR /app

ADD . /app/

# Add executable permissions to the script
RUN chmod +x /app/src/helm-post-renderer.py

RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "-u", "/app/src/server-controller.py"]