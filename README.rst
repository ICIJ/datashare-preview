About
=====

.. image:: https://circleci.com/gh/ICIJ/datashare-preview.png?style=shield&circle-token=7e42b81871950349431631c84419e83797b9d1c2
   :alt: Circle CI
   :target: https://circleci.com/gh/ICIJ/datashare-preview

This is an application that will take documents hashes/routing information as input
and serve previews/thumbnails for these documents.

It will cache the previews to avoid reprocessing images for each request.

Develop
-------
Before all, install dependency::

   sudo apt-get install libimage-exiftool-perl

Install dependencies to run the tests::

   sudo apt-get install inkscape scribus gnumeric

To develop, `install Pipenv <https://github.com/pypa/pipenv#installation>`_ then just run::

    pipenv install -d
    pipenv run python setup.py test
    pipenv run nosetests

To run the server::

    pipenv run pserve conf/development.ini


Release
-------

Mark the version (choose the correct one following `semver <https://semver.org/>`_)::

    make patch
    make minor
    make major

To build the Python package::

    make clean dist


Then build the docker image and publish it on Docker Hub::

    make docker-publish
