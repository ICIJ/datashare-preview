DOCKER_USER := icij
DOCKER_NAME := datashare-preview
DOCKER_TAG := latest
PWD := `pwd`

docker-run:
		docker run -it --rm \
		-p 5000:5000 \
		-e DISPLAY=$(DISPLAY) \
		-v $(PWD)/cache/:/var/www/app/cache/ \
		-v /tmp/.X11-unix:/tmp/.X11-unix $(DOCKER_NAME)

docker-build:
		docker build -t $(DOCKER_NAME) .

docker-tag:
		docker tag $(DOCKER_NAME) $(DOCKER_USER)/$(DOCKER_NAME):$(DOCKER_TAG)

docker-push:
		docker push $(DOCKER_USER)/$(DOCKER_NAME):$(DOCKER_TAG)
