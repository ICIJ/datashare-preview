FROM python:3.8

RUN apt-get update && apt-get install -y zlib1g-dev libjpeg-dev xterm \
  scribus libreoffice gnumeric inkscape xvfb qpdf \
  python3-pythonmagick poppler-utils libfile-mimeinfo-perl libimage-exiftool-perl

WORKDIR /tmp
ADD https://sno.phy.queensu.ca/~phil/exiftool/Image-ExifTool-11.11.tar.gz .

RUN gzip -dc Image-ExifTool-11.11.tar.gz | tar -xf - ; \
  cd Image-ExifTool-11.11 ; \
  perl Makefile.PL ; \
  make install

ARG DSPREVIEW_VERSION
WORKDIR /var/www/app
COPY dist/datashare-preview-$DSPREVIEW_VERSION.tar.gz conf/production.ini ./
RUN pip install datashare-preview-$DSPREVIEW_VERSION.tar.gz

RUN useradd -ms /bin/bash xterm
RUN mkdir --mode 777 /var/www/app/cache

# Fix a policy issue with ImageMagick (fixed on Ghostscript 9.24)
# @see https://stackoverflow.com/questions/52998331/imagemagick-security-policy-pdf-blocking-conversion
RUN sed -i '/disable ghostscript format types/,+6d' /etc/ImageMagick-6/policy.xml

USER xterm

ENV CACHE_PATH /var/www/app/cache
ENV DS_CONF_FILE conf/production.ini

CMD ["uvicorn", "dspreview.main:app", "--host", "0.0.0.0", "--port", "5000"]
