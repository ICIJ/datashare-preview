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

To develop, just run::

    virtualenv --python=python3 venv
    source venv/bin/activate
    python setup.py develop
    pip install -e ".[dev]"
    nosetests

To run the server::

    pserve conf/development.ini
