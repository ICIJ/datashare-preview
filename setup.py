import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

requires = [
    'preview-generator==0.12',
    'pyramid==1.10',
    'pyramid-auto-env==0.1.2',
    'waitress==1.4.3',
    'requests==2.22.0',
    'pygelf==0.3.6',
]

dev_requires = [
    'nose',
    'bumpversion',
    'pyramid-debugtoolbar',
    'pyramid-exclog',
    'vtk',
    'webtest'
]

setup(name='datashare-preview',
      version='0.7.1',
      description="App to show document previews with a backend Elasticsearch",
      long_description=README,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
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
      install_requires=requires,
      extras_require={
        'dev': dev_requires,
      },
      test_suite="nose.collector",
      entry_points={
        'paste.app_factory': [
            'main = dspreview:main',
        ],
      })
