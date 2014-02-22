import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-phantom-pdf',
    version='0.1',
    packages=['phantom_pdf', 'phantom_pdf_bin'],
    package_data={'phantom_pdf_bin': ['*.js']},
    include_package_data=True,
    license='BSD License',
    description='A simple app that let you create pdf files.',
    long_description=README,
    url='http://www.bananadesk.com/opensource/',
    author='Juan Carizza, Tim Zenderman, Emiliano Dalla Verde Marcozzi',
    author_email='juan.carizza@gmail.com, tim@bananadesk.com, edvm@fedoraproject.org',
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
