DOCKER_USER := icij
DOCKER_NAME := datashare-preview
PWD := `pwd`
CURRENT_VERSION ?= `pipenv run python setup.py --version`

clean:
		find . -name "*.pyc" -exec rm -rf {} \;
		rm -rf dist *.egg-info __pycache__ .eggs

install: install-virtualenv

dist:
		pipenv run python setup.py sdist

install-virtualenv:
		# Check if venv folder is already created and create it
		pipenv install

run:
		pipenv run uvicorn dspreview.main:app --reload --host 0.0.0.0 --port 5000

minor:
		pipenv run bump2version --commit --tag --current-version ${CURRENT_VERSION} minor setup.py

major:
		pipenv run bump2version --commit --tag --current-version ${CURRENT_VERSION} major setup.py

patch:
		pipenv run bump2version --commit --tag --current-version ${CURRENT_VERSION} patch setup.py

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
