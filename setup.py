from setuptools import setup, find_packages

version = '0.0.0'

install_requires = [
    'setuptools',
    'isotoma.recipe.gocaptain',
    'simplejson',
    'netaddr',
    'pysqlite',
    'epsilon>=0.6.0',
    'axiom',
    #PIL and tagpy also, but they don't work in here
    ]

try:
    # collections.OrderedDict is new in Python 2.7
    from collections import OrderedDict
except ImportError:
    install_requires.append('ordereddict')

try:
    # uuid is new in Python 2.5
    import uuid
except ImportError:
    install_requires.append('uuid')


setup(
    name = 'squeal',
    version = version,
    description = "Jukebox for Squeezebox players, with spotify support.",
    url = "http://squealserver.com/",
    long_description = open("README.rst").read() + "\n" + \
                       open("CHANGES.txt").read(),
    keywords = "squeezebox squeal spotify",
    author = "Doug Winter",
    author_email = "doug.winter@isotoma.com",
    license="Apache Software License",
    package_dir = {'': 'src'},
    packages = find_packages(exclude=['ez_setup']),
    package_data = {
        '': ['README.rst', 'CHANGES.txt'],
    },
    include_package_data = True,
    zip_safe = False,
    install_requires = install_requires,
)
