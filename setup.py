import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-phantom-pdf',
    version='0.3',
    packages=['phantom_pdf', 'phantom_pdf_bin'],
    package_data={'phantom_pdf_bin': ['*.js']},
    include_package_data=True,
    license='BSD License',
    description='A simple django app for creating pdf files.',
    long_description=README,
    url='https://github.com/BananaDesk/django-phantom-pdf',
    author='Juan Carizza, Tim Zenderman, Emiliano Dalla Verde Marcozzi',
    author_email='juan.carizza@gmail.com, tzenderman@gmail.com, edvm@fedoraproject.org',
    download_url='https://github.com/BananaDesk/django-phantom-pdf/archive/v0.3.tar.gz',
    classifiers=[
            'Environment :: Web Environment',
            'Framework :: Django',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Topic :: Internet :: WWW/HTTP',
            "Topic :: Utilities",
        ],
)
