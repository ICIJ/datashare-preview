DOCKER_USER := icij
DOCKER_NAME := datashare-preview
VIRTUALENV := venv/
PWD := `pwd`
CURRENT_VERSION ?= `python setup.py --version`

clean:
		find . -name "*.pyc" -exec rm -rf {} \;
		rm -rf dist *.egg-info __pycache__

install: install-virtualenv install-pip

dist:
		python setup.py sdist

install-virtualenv:
		# Check if venv folder is already created and create it
		if [ ! -d venv ]; then virtualenv $(VIRTUALENV) --python=python3 --no-site-package --distribute; fi

install-pip:
		. $(VIRTUALENV)bin/activate; pip install -e ".[dev]"

run:
		. $(VIRTUALENV)bin/activate; pserve conf/development.ini --reload

minor:
		bumpversion --commit --tag --current-version ${CURRENT_VERSION} minor setup.py --allow-dirty

major:
		. $(VIRTUALENV)bin/activate; bumpversion --commit --tag --current-version ${CURRENT_VERSION} major setup.py

patch:
		bumpversion --commit --tag --current-version ${CURRENT_VERSION} patch setup.py

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
