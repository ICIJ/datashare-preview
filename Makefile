DOCKER_USER := icij
DOCKER_NAME := datashare-preview
PWD := `pwd`
CURRENT_VERSION ?= `poetry version -s`
SEMVERS := major minor patch

install: install_poetry

install_poetry:
		poetry install --with dev

run:
		poetry run uvicorn dspreview.main:app --reload --host 0.0.0.0 --port 5000

test:
		poetry run nosetests

clean:
		find . -name "*.pyc" -exec rm -rf {} \;
		rm -rf dist *.egg-info __pycache__ .eggs
dist:
		poetry build


tag_version: 
		git commit -m "build: bump to ${CURRENT_VERSION}" pyproject.toml
		git tag ${CURRENT_VERSION}

$(SEMVERS):
		poetry version $@
		$(MAKE) tag_version

set_version:
		poetry version ${CURRENT_VERSION}
		$(MAKE) tag_version

docker-run:
		docker run -it --rm \
		-p 5000:5000 \
		-e DISPLAY=$(DISPLAY) \
		-v $(PWD)/cache/:/var/www/app/cache/ \
		-v /tmp/.X11-unix:/tmp/.X11-unix $(DOCKER_NAME)

docker-build: dist
		docker build --build-arg DSPREVIEW_VERSION=$(CURRENT_VERSION) -t $(DOCKER_NAME) .

docker-tag:
		docker tag $(DOCKER_NAME) $(DOCKER_USER)/$(DOCKER_NAME):${CURRENT_VERSION}

docker-push:
		docker push $(DOCKER_USER)/$(DOCKER_NAME):${CURRENT_VERSION}

docker-publish: docker-build docker-tag docker-push
