import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

setup(name='datashare-preview',
      version='1.0.0',
      description="App to show document previews with a backend Elasticsearch",
      long_description=README,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: FastAPI",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      keywords='icij, elasticsearch, preview',
      author='Pierre Romera, Bruno Thomas',
      author_email='promera@icij.org, bthomas@icij.org',
      url='https://github.com/ICIJ/datashare-preview',
      license='LICENSE',
      packages=find_packages(exclude=("*.tests", "*.tests.*", "tests.*", "tests", "*.test_utils")),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'preview-generator==0.29',
        'pygelf==0.3.6',
        'fastapi',
        'pydantic',
        'aiofiles',
        'fastapi-utils',
        'httpx==0.23.0',
        'uvicorn[standard]',
     ],
      extras_require={
        'dev': [
            'bumpversion==0.5.3',
            'respx',
            'nose',
            'requests'
        ],
      },
      test_suite="nose.collector",
      entry_points={
        'paste.app_factory': [
            'main = dspreview.main:app',
        ],
      })
