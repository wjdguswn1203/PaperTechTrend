all:
	uvicorn app:app --host 0.0.0.0 --port 3000 --reload &
pre:
	source .venv/bin/activate
run:
	uvicorn app:app --host 0.0.0.0 --port 3000 --reload &
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