all: build run k8init appsec appdep appsvc getdep getsvc getpod
restart: delsec delsvc deldep delpod appsec appdep appsvc appsec getdep getsvc getpod
stop: delsec delsvc deldep delpod
build:
	docker build -t nodejs .
run:
	docker run -it -d -p 8500:8500 -p 8000:8000 --name nodejs --env-file .env nodejs
exec:
	docker exec -it nodejs /bin/bash
logs:
	docker logs nodejs
ps:
	docker ps -a
img:
	docker images
rm:
	docker rm -f $$(docker ps -aq)
rmi:
	docker rmi -f $$(docker images -q)
k8init:
	docker commit nodejs nodejsapi
	docker tag nodejsapi wjdguswn1203/nodejsapi
	docker push wjdguswn1203/nodejsapi
	docker rm -f $$(docker ps -aq)
	docker rmi wjdguswn1203/nodejsapi
	docker rmi -f $$(docker images -q)
getnode:
	kubectl get nodes
appdep:
	kubectl apply -f deployment.yaml
appsvc:
	kubectl apply -f service.yaml
appsec:
	kubectl apply -f secret.yaml
appcon:
	kubectl apply -f bastion-config.yaml
getdep:
	kubectl get deployment
getsvc:
	kubectl get svc -o wide
getpod:
	kubectl get pod -o wide
getsec:
	kubectl get secret -o wide
delsvc:
	kubectl delete svc nodejsapi-service 
deldep:
	kubectl delete deployment nodejsapi
delsec:
	kubectl delete secret nodejsapi-secret
delpod:
	kubectl get pod | grep nodejsapi | awk '{print $$1}' | xargs -I {} kubectl delete pod {} --force
desdep:
	kubectl describe deployment nodejsapi
dessvc:
	kubectl describe svc nodejsapi-service
despod:
	kubectl describe pod nodejsapi