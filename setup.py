'''SpazUtils setup.py'''

import re
from os import path
from setuptools import setup

packageName = 'SpazUtils'
with open(path.join(path.abspath(path.dirname(__file__)), 'README.rst'), encoding='utf-8') as fp:
    README = fp.read()
# with open(path.join(path.abspath(path.dirname(__file__)), packageName, 'info.py'), encoding='utf-8') as fp:
#     VERSION = re.search("__version__ = '([^']+)'", fp.read()).group(1)

VERSION = '0.0.3'

setup(
    author='Lil_SpazJoekp',
    author_email='lilspazjoekp@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    description=('Utilities for Automating Moderation on Reddit'),
    download_url = 'https://github.com/LilSpazJoekp/SpazUtils/archive/0.0.3.tar.gz',
    install_requires=[
        'discord.py>=1.0.1',
        'praw>=6.1.1',
        'prawcore>=1.0.1',
        'psycopg2_binary>=2.7.7',
        'requests>=2.21.0',
        'timeago>=1.0.9',
        'typing>=3.6.6',
        'termcolor>=1.1.0'
    ],
    keywords='spaz utils utilities',
    license='gpl-3.0',
    long_description=README,
    name=packageName,
    url = 'https://github.com/user/SpazUtils',
    version=VERSION,
)