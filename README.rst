About
=====

.. image:: https://github.com/icij/datashare-preview/actions/workflows/main.yml/badge.svg?branch=master
   :alt: Github Actions
   :target: https://github.com/icij/datashare-preview/actions/

This is an application that will take documents hashes/routing information as input
and serve previews/thumbnails for these documents.

It will cache the previews to avoid reprocessing images for each request.

Develop
-------
Install system dependencies once and for all::

    make install_dependencies
    
To develop, [install Poetry](https://python-poetry.org/docs/#installation) then just run::

    make install
    make test

To run the server::

    make run


Release
-------

Mark the version (choose the correct one following [semver](https://semver.org/))::

    make patch
    make minor
    make major

To set a specific version use this command:

    make set_version CURRENT_VERSION=X.Y.Z
    
To build the Python package::

    make clean dist

To build the docker image and publish it on Docker Hub::

    make docker-publish


**Note**: Datashare Preview is a multi-platform build. You might need to setup your environment for 
multi-platform using the `make docker-setup-multiarch` command. Read more 
[on Docker documentation](https://docs.docker.com/build/building/multi-platform/). 
