import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

requires = [
    'preview-generator',
    'Flask==1.0.2',
    'pyramid==1.10',
    'waitress==1.3.1',
    'flask-cors',
    'requests'
]

setup(name='datashare-preview',
      version='0.1.3',
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
      test_suite="nose.collector",
      entry_points={
        'paste.app_factory': [
            'main = dspreview:main',
        ],
      }
      )