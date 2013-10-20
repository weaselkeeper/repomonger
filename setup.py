#!/usr/bin/env python
"""
Setup script.
"""

from distutils.core import setup


setup(name = "repomonger",
    version = "0.2",
    description = "Simple yum repo clone/copy/assembler ",
    long_description = "clone/copy/assemble yum repos",
    author = "Jim Richardson",
    author_email = 'weaselkeeper@gmail.com',
    url = "https://github.com/weaselkeeper/repomonger",
    download_url = "https://github.com/weaselkeeper/repomonger",
    platforms = ['any'],
    license = "GPLv2",
    package_dir = {'repomonger': 'src' },
    packages = ['repomonger'],
    classifiers = [
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'Programming Language :: Python'],
)
