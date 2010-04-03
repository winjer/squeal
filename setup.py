from setuptools import setup, find_packages

version = '0.0.0'

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
    packages = find_packages(exclude=['ez_setup']),
    package_data = {
        '': ['README.rst', 'CHANGES.txt'],
    },
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'setuptools',
        'isotoma.recipe.gocaptain',
        'spotify',
        'simplejson',
        'netaddr',
        'zope.interface',
        'twisted',
        'pysqlite',
        'Nevow',
        'Axiom',
        'Epsilon',
        #PIL and tagpy also, but they don't work in here
    ],
)

