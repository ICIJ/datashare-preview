About
=====

This is an application that will take documents hashes/routing information as input
and serve previews/thumbnails for these documents.

It will cache the previews to avoid reprocessing images for each request.

Develop
-------

To develop, just run::

    virtualenv --python=python3 venv
    source venv/bin/activate
    python setup.py develop
    pip install -r dev-requirements.txt
    nosetests

To run the server::

    pserve conf/development.ini
