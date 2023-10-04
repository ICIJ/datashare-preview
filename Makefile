DOCKER_USER := icij
DOCKER_NAME := datashare-preview
PWD := `pwd`
CURRENT_VERSION ?= `poetry version -s`
SEMVERS := major minor patch

install_dependencies:
	sudo apt-get update && \
		sudo apt-get -y install \
			poppler-utils libfile-mimeinfo-perl libimage-exiftool-perl \
			ghostscript libsecret-1-0 zlib1g-dev libjpeg-dev imagemagick libmagic1 webp \
			gnumeric libreoffice
install: install_poetry

install_poetry:
		poetry install --with dev

run:
		poetry run uvicorn dspreview.main:app --reload --host 0.0.0.0 --port 5000

test:
		poetry run pytest

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

docker-setup-multiarch:
		docker run --privileged --rm multiarch/qemu-user-static --reset -p yes
		docker buildx create --use

docker-publish: dist
		docker buildx build \
		 	--build-arg DSPREVIEW_VERSION=$(CURRENT_VERSION) \
			--platform linux/amd64,linux/arm64 \
			-t $(DOCKER_USER)/$(DOCKER_NAME):${CURRENT_VERSION} \
			-t $(DOCKER_USER)/$(DOCKER_NAME):latest \
			--push .
