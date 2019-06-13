DOCKER_USER := icij
DOCKER_NAME := datashare-preview
DOCKER_TAG := latest
VIRTUALENV := venv/
PWD := `pwd`

clean:
		find . -name "*.pyc" -exec rm -rf {} \;

install: install_virtualenv install_pip

install_virtualenv:
		# Check if venv folder is already created and create it
		if [ ! -d venv ]; then virtualenv $(VIRTUALENV) --python=python3 --no-site-package --distribute; fi

install_pip:
		. $(VIRTUALENV)bin/activate; pip install -r requirements.txt

run:
		. $(VIRTUALENV)bin/activate; FLASK_ENV=development flask run --host=0.0.0.0 --port=5050 

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

docker-publish: docker-build docker-tag docker-push
