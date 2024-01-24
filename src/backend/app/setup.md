- Build docker image: `docker build -f Dockerfile -t flask-server-api:latest .`
- Add deployment: `kubectl apply -f deployment.yaml`
- Delete deployment: `kubectl delete -f deployment.yaml`
- Check ServiceAccount perms: `kubectl auth can-i list pods --as=system:serviceaccount:default:my-service-account -n default`
- Connect to Docker for Desktop shell:
`docker run -it --rm --privileged --pid=host alpine nsenter -t 1 -m -u -n -i sh`
