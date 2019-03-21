DOCKER_USER := icij
DOCKER_NAME := datashare-preview
PWD := `pwd`

install:
	yarn

docker-run:
		docker run -it --rm \
		-p 5000:5000 \
    -e DISPLAY=$(DISPLAY) \
		-v $(PWD)/cache/:/var/www/app/cache/ \
    -v /tmp/.X11-unix:/tmp/.X11-unix $(DOCKER_NAME) \
		env FLASK_APP=app.py flask run --host=0.0.0.0

docker-build:
		docker build -t $(DOCKER_NAME) .

docker-tag:
		docker tag $(DOCKER_NAME) $(DOCKER_USER)/$(DOCKER_NAME):$(DOCKER_TAG)

docker-push:
		docker push $(DOCKER_USER)/$(DOCKER_NAME):$(DOCKER_TAG)
