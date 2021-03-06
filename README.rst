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

To develop, [install Pipenv](https://github.com/pypa/pipenv#installation) then just run::

    pipenv install -d
    pipenv run python setup.py test

To run the server::

    pipenv run pserve conf/development.ini


Release
-------

Mark the version (choose the correct one following [semver](https://semver.org/))::

    make patch
    make minor
    make major

To build the Python package::

    make clean dist


Then build the docker image and publish it on Docker Hub::

    make docker-publish
