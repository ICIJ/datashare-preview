FROM python:3.13-bookworm AS requirements

WORKDIR /tmp

RUN pip install poetry==1.3
COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM python:3.13-bookworm

RUN apt-get update && apt-get install -y \
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

WORKDIR /tmp
ADD https://exiftool.org/Image-ExifTool-13.39.tar.gz .

RUN gzip -dc Image-ExifTool-13.39.tar.gz | tar -xf - ; \
  cd Image-ExifTool-13.39 ; \
  perl Makefile.PL ; \
  make install

WORKDIR /var/www/app

COPY --from=requirements /tmp/requirements.txt .
RUN  pip install --no-cache-dir --upgrade -r /var/www/app/requirements.txt

COPY . .

RUN useradd -ms /bin/bash xterm
RUN mkdir --mode 777 /var/www/app/cache

# fix DNG decoding using dcraw
# @see https://stackoverflow.com/questions/54036071/imagemagic-gives-delegate-failed-ufraw-batch
# @see http://www.kevinludlow.com/blog/Configuring_ImageMagick_RAW_Delegates_with_DCRAW_and_UFRAWBatch/1240258/
RUN sed -i '/<delegate decode="dng:decode"/c\<delegate decode="dng:decode" command="&quot;dcraw&quot; -c &quot;%i&quot; > &quot;%u.ppm&quot;"/>' \
  /etc/ImageMagick-*/delegates.xml

USER xterm

ENV CACHE_PATH=/var/www/app/cache
ENV DS_CONF_FILE=/var/www/app/conf/production.ini
ENV HOST=0.0.0.0
ENV PORT=5000

CMD ["sh", "-c", "uvicorn dspreview.main:app --proxy-headers --host $HOST --port $PORT"]