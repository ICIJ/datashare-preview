FROM python:3.7

ARG DSPREVIEW_VERSION

RUN apt-get update && apt-get install -y zlib1g-dev libjpeg-dev xterm \
  scribus libreoffice inkscape xvfb qpdf \
  python3-pythonmagick poppler-utils libfile-mimeinfo-perl

WORKDIR /tmp
ADD https://sno.phy.queensu.ca/~phil/exiftool/Image-ExifTool-11.11.tar.gz .

RUN gzip -dc Image-ExifTool-11.11.tar.gz | tar -xf - ; \
  cd Image-ExifTool-11.11 ; \
  perl Makefile.PL ; \
  make install

WORKDIR /var/www/app
COPY production.ini .
COPY dist/datashare-preview-$DSPREVIEW_VERSION.tar.gz .
RUN pip install datashare-preview-$DSPREVIEW_VERSION.tar.gz

RUN useradd -ms /bin/bash xterm
RUN mkdir --mode 777 /var/www/app/cache

USER xterm

ENV CACHE_PATH /var/www/app/cache

CMD [ "pserve", "production.ini" ]
