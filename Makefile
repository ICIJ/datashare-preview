HOST := 0.0.0.0
PORT := 5000
DOCKER_USER := icij
DOCKER_NAME := datashare-preview
PWD := `pwd`
CURRENT_VERSION ?= `poetry version -s`
SEMVERS := major minor patch

install_dependencies:
	sudo apt-get update && sudo apt-get install -y \
			dcraw \
			ffmpeg \
			ghostscript \
			gnumeric \
			imagemagick \
			inkscape \
			libfile-mimeinfo-perl \
			libgomp1 \
			libimage-exiftool-perl \
			libjpeg-dev \
			libmagic1 \
			libreoffice \
			libsecret-1-0 \
			poppler-utils \
			qpdf \
			scribus \
			webp \
			xterm \
			xvfb \
			zlib1g-dev
	
install: install_dependencies install_poetry

install_poetry:
		poetry install --with dev

run:
		poetry run uvicorn dspreview.main:app --reload --host $(HOST) --port $(PORT)

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

docker-publish:
		docker buildx build \
			--platform linux/amd64,linux/arm64 \
			-t $(DOCKER_USER)/$(DOCKER_NAME):${CURRENT_VERSION} \
			-t $(DOCKER_USER)/$(DOCKER_NAME):latest \
			--push .
