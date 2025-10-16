FROM python:3.11-bullseye as requirements

WORKDIR /tmp

RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM python:3.11-bullseye

RUN apt-get update && apt-get install -y \
      xterm xvfb qpdf \
      poppler-utils libfile-mimeinfo-perl libimage-exiftool-perl \
      ghostscript zlib1g-dev libjpeg-dev imagemagick libmagic1 webp \
      scribus libreoffice gnumeric inkscape libgomp1

WORKDIR /tmp
ADD https://exiftool.org/Image-ExifTool-12.52.tar.gz .

RUN gzip -dc Image-ExifTool-12.52.tar.gz | tar -xf - ; \
  cd Image-ExifTool-12.52 ; \
  perl Makefile.PL ; \
  make install

WORKDIR /var/www/app

COPY . .
COPY --from=requirements /tmp/requirements.txt .
RUN  pip install --no-cache-dir --upgrade -r /var/www/app/requirements.txt

RUN useradd -ms /bin/bash xterm
RUN mkdir --mode 777 /var/www/app/cache

# Fix a policy issue with ImageMagick (fixed on Ghostscript 9.24)
# @see https://stackoverflow.com/questions/52998331/imagemagick-security-policy-pdf-blocking-conversion
RUN sed -i '/disable ghostscript format types/,+6d' /etc/ImageMagick-6/policy.xml

USER xterm

ENV CACHE_PATH=/var/www/app/cache
ENV DS_CONF_FILE=/var/www/app/conf/production.ini

CMD ["uvicorn", "dspreview.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "5000"]